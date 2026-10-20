const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const querystring = require('querystring');

const CONFIG_PATH = path.resolve('C:/Users/Admin/.buzz/credentials/linkedin_config.json');

class LinkedInApi {
    constructor() {
        this.config = this.loadConfig();
    }

    loadConfig() {
        if (!fs.existsSync(CONFIG_PATH)) {
            const defaultConfig = {
                app_id: "263861372",
                client_id: "86vk0dkiykfjsz",
                client_secret: "",
                redirect_uri: "http://localhost:8080/callback",
                access_token: "",
                expires_at: 0,
                refresh_token: "",
                refresh_token_expires_at: 0,
                user_urn: "",
                user_name: "",
                organization_urn: "",
                organization_name: "Minh Van Logistics",
                updated_at: new Date().toISOString()
            };
            fs.mkdirSync(path.dirname(CONFIG_PATH), { recursive: true });
            fs.writeFileSync(CONFIG_PATH, JSON.stringify(defaultConfig, null, 2), 'utf8');
            return defaultConfig;
        }
        return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    }

    saveConfig() {
        this.config.updated_at = new Date().toISOString();
        fs.writeFileSync(CONFIG_PATH, JSON.stringify(this.config, null, 2), 'utf8');
    }

    async ensureAccessToken() {
        const now = Date.now();
        if (this.config.access_token && this.config.expires_at > now + 3600 * 1000) {
            return this.config.access_token;
        }

        if (this.config.refresh_token && this.config.client_id && this.config.client_secret) {
            console.log("[LinkedIn] Đang làm mới Access Token từ Refresh Token...");
            try {
                const postData = querystring.stringify({
                    grant_type: 'refresh_token',
                    refresh_token: this.config.refresh_token,
                    client_id: this.config.client_id,
                    client_secret: this.config.client_secret
                });
                const res = await this.requestRaw('https://www.linkedin.com/oauth/v2/accessToken', 'POST', {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }, postData);

                if (res.access_token) {
                    this.config.access_token = res.access_token;
                    this.config.expires_at = Date.now() + (parseInt(res.expires_in, 10) || 5184000) * 1000;
                    if (res.refresh_token) {
                        this.config.refresh_token = res.refresh_token;
                        this.config.refresh_token_expires_at = Date.now() + (parseInt(res.refresh_token_expires_in, 10) || 31536000) * 1000;
                    }
                    this.saveConfig();
                    return this.config.access_token;
                }
            } catch (err) {
                console.warn("[LinkedIn] Không thể tự làm mới qua refresh token:", err.message);
            }
        }

        if (this.config.access_token && this.config.expires_at > now) {
            return this.config.access_token;
        }

        throw new Error("LinkedIn Access Token đã hết hạn hoặc chưa được cấu hình. Vui lòng chạy: linkedin-control auth");
    }

    getHeaders(token) {
        return {
            'Authorization': `Bearer ${token}`,
            'X-Restli-Protocol-Version': '2.0.0',
            'LinkedIn-Version': '202601',
            'Content-Type': 'application/json'
        };
    }

    // Lấy thông tin cá nhân người dùng (OpenID / UserInfo)
    async getProfile() {
        const token = await this.ensureAccessToken();
        const res = await this.requestRaw('https://api.linkedin.com/v2/userinfo', 'GET', {
            'Authorization': `Bearer ${token}`
        });
        if (res.sub) {
            this.config.user_urn = `urn:li:person:${res.sub}`;
            this.config.user_name = res.name || `${res.given_name || ''} ${res.family_name || ''}`.trim();
            this.saveConfig();
        }
        return res;
    }

    // Lấy danh sách các Organization/Company Page được quyền quản trị
    async getOrganizations() {
        const token = await this.ensureAccessToken();
        const res = await this.requestRaw('https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee', 'GET', {
            'Authorization': `Bearer ${token}`,
            'X-Restli-Protocol-Version': '2.0.0'
        });
        return res;
    }

    // Khởi tạo và upload ảnh (Image)
    async uploadImage(imagePath, ownerUrn) {
        const token = await this.ensureAccessToken();
        if (!fs.existsSync(imagePath)) {
            throw new Error(`File ảnh không tồn tại: ${imagePath}`);
        }

        const owner = ownerUrn || this.config.organization_urn || this.config.user_urn;
        if (!owner) {
            throw new Error("Chưa xác định được owner URN (Organization URN hoặc Person URN)");
        }

        // Bước 1: Khởi tạo upload
        const initPayload = {
            initializeUploadRequest: {
                owner: owner
            }
        };

        const initRes = await this.requestRaw('https://api.linkedin.com/rest/images?action=initializeUpload', 'POST', this.getHeaders(token), JSON.stringify(initPayload));
        
        const uploadUrl = initRes?.value?.uploadUrl;
        const imageUrn = initRes?.value?.image;

        if (!uploadUrl || !imageUrn) {
            throw new Error(`Lỗi khởi tạo upload ảnh: ${JSON.stringify(initRes)}`);
        }

        // Bước 2: Upload binary ảnh lên uploadUrl
        const ext = path.extname(imagePath).toLowerCase();
        const contentType = (ext === '.png') ? 'image/png' : 'image/jpeg';
        const fileData = fs.readFileSync(imagePath);

        await this.uploadBinary(uploadUrl, fileData, contentType);

        return {
            imageUrn,
            owner
        };
    }

    // Khởi tạo và upload tài liệu PDF (Carousel)
    async uploadDocument(pdfPath, ownerUrn, title = "Tài liệu chia sẻ") {
        const token = await this.ensureAccessToken();
        if (!fs.existsSync(pdfPath)) {
            throw new Error(`File PDF không tồn tại: ${pdfPath}`);
        }

        const owner = ownerUrn || this.config.organization_urn || this.config.user_urn;
        if (!owner) {
            throw new Error("Chưa xác định được owner URN");
        }

        // Bước 1: Khởi tạo upload tài liệu
        const initPayload = {
            initializeUploadRequest: {
                owner: owner
            }
        };

        const initRes = await this.requestRaw('https://api.linkedin.com/rest/documents?action=initializeUpload', 'POST', this.getHeaders(token), JSON.stringify(initPayload));
        
        const uploadUrl = initRes?.value?.uploadUrl;
        const documentUrn = initRes?.value?.document;

        if (!uploadUrl || !documentUrn) {
            throw new Error(`Lỗi khởi tạo upload PDF: ${JSON.stringify(initRes)}`);
        }

        // Bước 2: Upload binary PDF
        const fileData = fs.readFileSync(pdfPath);
        await this.uploadBinary(uploadUrl, fileData, 'application/pdf');

        return {
            documentUrn,
            title,
            owner
        };
    }

    // Tạo bài viết (Posts API)
    async createPost({ authorUrn, commentary, mediaUrn, mediaTitle, articleUrl, articleTitle, articleDesc }) {
        const token = await this.ensureAccessToken();
        const author = authorUrn || this.config.organization_urn || this.config.user_urn;
        if (!author) {
            throw new Error("Thiếu author URN để xuất bản bài viết");
        }

        const payload = {
            author: author,
            commentary: commentary,
            visibility: "PUBLIC",
            distribution: {
                feedDistribution: "MAIN_FEED",
                targetEntities: [],
                thirdPartyDistributionChannels: []
            },
            lifecycleState: "PUBLISHED",
            isReshareDisabledByAuthor: false
        };

        if (mediaUrn) {
            payload.content = {
                media: {
                    id: mediaUrn,
                    title: mediaTitle || "Minh Vân Logistics"
                }
            };
        } else if (articleUrl) {
            payload.content = {
                article: {
                    source: articleUrl,
                    title: articleTitle || commentary.split('\n')[0].slice(0, 100),
                    description: articleDesc || ""
                }
            };
        }

        const res = await this.requestRaw('https://api.linkedin.com/rest/posts', 'POST', this.getHeaders(token), JSON.stringify(payload), true);
        return res;
    }

    // Helper upload file nhị phân (PUT)
    uploadBinary(targetUrl, buffer, contentType) {
        return new Promise((resolve, reject) => {
            const parsed = new URL(targetUrl);
            const lib = parsed.protocol === 'https:' ? https : http;
            const req = lib.request({
                hostname: parsed.hostname,
                port: parsed.port || (parsed.protocol === 'https:' ? 443 : 80),
                path: parsed.pathname + parsed.search,
                method: 'PUT',
                headers: {
                    'Content-Type': contentType,
                    'Content-Length': buffer.length
                }
            }, (res) => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    resolve({ status: res.statusCode });
                } else {
                    let d = '';
                    res.on('data', c => d += c);
                    res.on('end', () => reject(new Error(`Upload binary thất bại (${res.statusCode}): ${d}`)));
                }
            });
            req.on('error', reject);
            req.write(buffer);
            req.end();
        });
    }

    // Helper request chung
    requestRaw(targetUrl, method, headers, postData = null, returnHeaders = false) {
        return new Promise((resolve, reject) => {
            const parsed = new URL(targetUrl);
            const req = https.request({
                hostname: parsed.hostname,
                port: parsed.port || 443,
                path: parsed.pathname + parsed.search,
                method,
                headers
            }, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    const xRestliId = res.headers['x-restli-id'] || res.headers['x-linkedin-id'];
                    try {
                        const json = data ? JSON.parse(data) : {};
                        if (returnHeaders) {
                            resolve({ data: json, headers: res.headers, postId: xRestliId, statusCode: res.statusCode });
                        } else {
                            resolve(json);
                        }
                    } catch (e) {
                        if (returnHeaders) {
                            resolve({ raw: data, headers: res.headers, postId: xRestliId, statusCode: res.statusCode });
                        } else {
                            resolve({ raw: data, statusCode: res.statusCode, postId: xRestliId });
                        }
                    }
                });
            });
            req.on('error', reject);
            if (postData) req.write(postData);
            req.end();
        });
    }
}

module.exports = new LinkedInApi();
