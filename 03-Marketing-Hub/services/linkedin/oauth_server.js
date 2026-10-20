const http = require('http');
const https = require('https');
const url = require('url');
const querystring = require('querystring');
const { exec } = require('child_process');
const linkedinApi = require('./linkedin_api');

const PORT = 53684;
const DEFAULT_SCOPES = [
    'openid',
    'profile',
    'email',
    'w_member_social'
].join(' ');

async function startOAuthFlow(customScope = null) {
    const config = linkedinApi.config;
    if (!config.client_id || !config.client_secret) {
        console.error("❌ Chưa có client_id hoặc client_secret trong linkedin_config.json");
        console.error("Vui lòng cấu hình qua: linkedin-control set-credentials --client-id <id> --client-secret <secret>");
        process.exit(1);
    }

    const scopeArgIdx = process.argv.indexOf("--scope");
    const cliScope = scopeArgIdx !== -1 && process.argv[scopeArgIdx + 1] ? process.argv[scopeArgIdx + 1] : null;
    const requestedScope = customScope || cliScope || config.requested_scopes || DEFAULT_SCOPES;

    const state = Math.random().toString(36).substring(2) + Date.now().toString(36);
    const redirectUri = config.redirect_uri || `http://localhost:${PORT}/callback`;

    const authUrl = `https://www.linkedin.com/oauth/v2/authorization?` + querystring.stringify({
        response_type: 'code',
        client_id: config.client_id,
        redirect_uri: redirectUri,
        state: state,
        scope: requestedScope
    });

    const server = http.createServer(async (req, res) => {
        const parsedUrl = url.parse(req.url, true);
        if (parsedUrl.pathname === '/callback') {
            const { code, state: returnedState, error, error_description } = parsedUrl.query;

            if (error) {
                res.writeHead(400, { 'Content-Type': 'text/html; charset=utf-8' });
                res.end(`<h2>❌ Lỗi xác thực LinkedIn:</h2><p>${error_description || error}</p>`);
                console.error(`[OAuth] Lỗi xác thực: ${error_description || error}`);
                server.close();
                process.exit(1);
                return;
            }

            if (!code) {
                res.writeHead(400, { 'Content-Type': 'text/html; charset=utf-8' });
                res.end(`<h2>❌ Không tìm thấy authorization code</h2>`);
                return;
            }

            try {
                console.log("\n🔄 Đang đổi Authorization Code lấy Access Token...");
                const postData = querystring.stringify({
                    grant_type: 'authorization_code',
                    code: code,
                    redirect_uri: redirectUri,
                    client_id: config.client_id,
                    client_secret: config.client_secret
                });

                const tokenRes = await linkedinApi.requestRaw('https://www.linkedin.com/oauth/v2/accessToken', 'POST', {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }, postData);

                if (!tokenRes.access_token) {
                    throw new Error(`Phản hồi Token không hợp lệ: ${JSON.stringify(tokenRes)}`);
                }

                config.access_token = tokenRes.access_token;
                config.expires_at = Date.now() + (parseInt(tokenRes.expires_in, 10) || 5184000) * 1000;
                if (tokenRes.refresh_token) {
                    config.refresh_token = tokenRes.refresh_token;
                    config.refresh_token_expires_at = Date.now() + (parseInt(tokenRes.refresh_token_expires_in, 10) || 31536000) * 1000;
                }

                linkedinApi.saveConfig();
                console.log("✅ Đã lưu Access Token (Hiệu lực: 60 ngày)!");

                // Lấy thông tin user
                try {
                    const profile = await linkedinApi.getProfile();
                    console.log(`👤 Người dùng: ${config.user_name} (${config.user_urn})`);
                } catch (e) {
                    console.warn("Lưu ý đọc profile:", e.message);
                }

                // Lấy thông tin organizations
                try {
                    const orgs = await linkedinApi.getOrganizations();
                    if (orgs?.elements && orgs.elements.length > 0) {
                        const firstOrg = orgs.elements[0].organizationalTarget;
                        if (firstOrg) {
                            config.organization_urn = firstOrg;
                            linkedinApi.saveConfig();
                            console.log(`🏢 Organization kết nối: ${firstOrg}`);
                        }
                    }
                } catch (e) {
                    console.warn("Lưu ý đọc organizations:", e.message);
                }

                res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
                res.end(`
                    <html>
                    <body style="font-family: system-ui, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; background: #f3f6f8;">
                        <div style="background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; max-width: 480px;">
                            <h1 style="color: #0a66c2;">🎉 Xác thực LinkedIn thành công!</h1>
                            <p style="color: #333; font-size: 16px;">Tài khoản đã được liên kết với hệ thống AI Agent trên Buzz.</p>
                            <p style="color: #666; font-size: 14px;">Bạn có thể đóng tab này lại và tiếp tục làm việc.</p>
                        </div>
                    </body>
                    </html>
                `);

                console.log("\n==================================================================");
                console.log("🎉 XÁC THỰC OAUTH LINKEDIN THÀNH CÔNG VÀ SẴN SÀNG SỬ DỤNG!");
                console.log("==================================================================");
                
                setTimeout(() => {
                    server.close();
                    process.exit(0);
                }, 2000);

            } catch (err) {
                res.writeHead(500, { 'Content-Type': 'text/html; charset=utf-8' });
                res.end(`<h2>❌ Lỗi:</h2><p>${err.message}</p>`);
                console.error("Lỗi hoàn tất OAuth:", err.message);
                server.close();
                process.exit(1);
            }
        }
    });

    server.listen(PORT, () => {
        console.log(`🌐 Máy chủ xác thực đang lắng nghe tại: http://localhost:${PORT}`);
        console.log(`🔗 Vui lòng mở đường dẫn sau trên trình duyệt để ủy quyền:`);
        console.log(`\n${authUrl}\n`);
        
        // Tự động mở trình duyệt mặc định
        exec(`start "" "${authUrl}"`, (err) => {
            if (err) console.log("Hãy copy link trên và dán vào trình duyệt của bạn.");
        });
    });
}

if (require.main === module) {
    startOAuthFlow();
}

module.exports = { startOAuthFlow };
