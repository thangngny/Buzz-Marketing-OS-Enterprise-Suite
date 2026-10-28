const https = require('https');
const querystring = require('querystring');
const fs = require('fs');
const path = require('path');

const CONFIG_PATH = path.resolve('C:/Users/Admin/.buzz/credentials/zalo_oa_config.json');

class ZaloOaApi {
    constructor() {
        this.config = this.loadConfig();
    }

    loadConfig() {
        if (!fs.existsSync(CONFIG_PATH)) {
            const defaultConfig = {
                app_id: "",
                secret_key: "",
                oa_id: "",
                access_token: "",
                refresh_token: "",
                expires_at: 0,
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

    // Tự động làm mới Access Token nếu sắp hết hạn
    async ensureAccessToken() {
        const now = Date.now();
        // Nếu token còn hạn trên 30 phút thì dùng tiếp
        if (this.config.access_token && this.config.expires_at > now + 30 * 60 * 1000) {
            return this.config.access_token;
        }

        if (!this.config.refresh_token || !this.config.app_id || !this.config.secret_key) {
            throw new Error("Thiếu cấu hình: app_id, secret_key hoặc refresh_token trong zalo_oa_config.json");
        }

        console.log("[Zalo-OA] Đang tự động làm mới Access Token qua Refresh Token...");
        const postData = querystring.stringify({
            app_id: this.config.app_id,
            grant_type: 'refresh_token',
            refresh_token: this.config.refresh_token
        });

        const res = await this.request('oauth.zaloapp.com', '/v4/oa/access_token', 'POST', {
            'Content-Type': 'application/x-www-form-urlencoded',
            'secret_key': this.config.secret_key
        }, postData);

        if (res.access_token) {
            this.config.access_token = res.access_token;
            this.config.refresh_token = res.refresh_token; // Refresh token mới 100%
            this.config.expires_at = Date.now() + (parseInt(res.expires_in, 10) || 86400) * 1000;
            this.saveConfig();
            console.log("[Zalo-OA] Làm mới Access Token thành công!");
            return this.config.access_token;
        } else {
            throw new Error(`Lỗi làm mới Token: ${JSON.stringify(res)}`);
        }
    }

    // Gửi tin nhắn CSKH (Tư vấn văn bản)
    async sendTextMessage(userId, text, quoteMessageId = null) {
        const token = await this.ensureAccessToken();
        const payload = {
            recipient: { user_id: userId },
            message: { text }
        };
        if (quoteMessageId) {
            payload.message.quote_message_id = quoteMessageId;
        }

        return await this.request('openapi.zalo.me', '/v3.0/oa/message/cs', 'POST', {
            'access_token': token,
            'Content-Type': 'application/json'
        }, JSON.stringify(payload));
    }

    // Gửi tin nhắn hình ảnh
    async sendImageMessage(userId, imageUrl, text = "") {
        const token = await this.ensureAccessToken();
        const payload = {
            recipient: { user_id: userId },
            message: {
                text: text || "Gửi bạn hình ảnh chi tiết:",
                attachment: {
                    type: "template",
                    payload: {
                        template_type: "media",
                        elements: [{
                            media_type: "image",
                            url: imageUrl
                        }]
                    }
                }
            }
        };

        return await this.request('openapi.zalo.me', '/v3.0/oa/message/cs', 'POST', {
            'access_token': token,
            'Content-Type': 'application/json'
        }, JSON.stringify(payload));
    }

    // Gửi thông báo ZNS theo số điện thoại
    async sendZns(phone, templateId, templateData = {}) {
        const token = await this.ensureAccessToken();
        let formattedPhone = phone.replace(/^0/, '84').replace(/^\+84/, '84');
        const payload = {
            phone: formattedPhone,
            template_id: templateId,
            template_data: templateData
        };

        return await this.request('business.openapi.zalo.me', '/message/template', 'POST', {
            'access_token': token,
            'Content-Type': 'application/json'
        }, JSON.stringify(payload));
    }

    // Lấy thông tin người dùng theo User ID
    async getProfile(userId) {
        const token = await this.ensureAccessToken();
        return await this.request('openapi.zalo.me', `/v3.0/oa/user/detail?data=${encodeURIComponent(JSON.stringify({ user_id: userId }))}`, 'GET', {
            'access_token': token
        });
    }

    // Lấy thông tin Official Account
    async getOaInfo() {
        const token = await this.ensureAccessToken();
        return await this.request('openapi.zalo.me', '/v2.0/oa/getoa', 'GET', {
            'access_token': token
        });
    }

    // Lấy danh sách người quan tâm (Followers)
    async getFollowers(offset = 0, count = 50) {
        const token = await this.ensureAccessToken();
        const query = querystring.stringify({ data: JSON.stringify({ offset, count }) });
        return await this.request('openapi.zalo.me', `/v3.0/oa/user/getlist?${query}`, 'GET', {
            'access_token': token
        });
    }

    // Lấy danh sách bài viết (Articles)
    async getArticles(offset = 0, limit = 10, type = 'normal') {
        const token = await this.ensureAccessToken();
        return await this.request('openapi.zalo.me', `/v2.0/article/getslice?offset=${offset}&limit=${limit}&type=${type}`, 'GET', {
            'access_token': token
        });
    }

    // Lấy chi tiết bài viết theo ID
    async getArticleDetail(articleId) {
        const token = await this.ensureAccessToken();
        return await this.request('openapi.zalo.me', `/v2.0/article/getdetail?id=${encodeURIComponent(articleId)}`, 'GET', {
            'access_token': token
        });
    }

    // Tạo bài viết mới trên OA
    async createArticle(articleData) {
        const token = await this.ensureAccessToken();
        const payload = {
            type: articleData.type || "normal",
            title: articleData.title,
            author: articleData.author || "Minh Vân Logistics",
            cover: articleData.cover,
            description: articleData.description,
            body: articleData.body || [],
            status: articleData.status || "show",
            comment: articleData.comment || "show"
        };
        if (articleData.related_medias) {
            payload.related_medias = articleData.related_medias;
        }

        return await this.request('openapi.zalo.me', '/v2.0/article/create', 'POST', {
            'access_token': token,
            'Content-Type': 'application/json'
        }, JSON.stringify(payload));
    }

    // Upload ảnh lấy URL ảnh bìa
    async uploadImage(imagePath) {
        const token = await this.ensureAccessToken();
        const fileBytes = fs.readFileSync(imagePath);
        const filename = path.basename(imagePath);
        const mime = filename.endsWith('.png') ? 'image/png' : 'image/jpeg';
        const blob = new Blob([fileBytes], { type: mime });
        const form = new FormData();
        form.append('file', blob, filename);

        const res = await fetch('https://openapi.zalo.me/v2.0/oa/upload/image', {
            method: 'POST',
            headers: { 'access_token': token },
            body: form
        });
        return await res.json();
    }

    // Tải video lên Zalo OA
    async uploadVideo(videoPath) {
        const token = await this.ensureAccessToken();
        const fileBytes = fs.readFileSync(videoPath);
        const filename = path.basename(videoPath);
        const blob = new Blob([fileBytes], { type: 'video/mp4' });
        const form = new FormData();
        form.append('file', blob, filename);

        const res = await fetch('https://openapi.zalo.me/v2.0/article/upload_video/preparevideo', {
            method: 'POST',
            headers: { 'access_token': token },
            body: form
        });
        const prep = await res.json();
        if (prep.error !== 0 || !prep.data || !prep.data.token) {
            throw new Error(`Lỗi upload video Zalo OA: ${JSON.stringify(prep)}`);
        }

        const videoToken = prep.data.token;
        // Chờ Zalo xử lý video (poll verify tối đa 60s)
        for (let i = 0; i < 20; i++) {
            await new Promise(r => setTimeout(r, 2000));
            const vRes = await fetch('https://openapi.zalo.me/v2.0/article/upload_video/verify', {
                method: 'GET',
                headers: {
                    'access_token': token,
                    'token': videoToken
                }
            });
            const vData = await vRes.json();
            if (vData.error === 0 && vData.data && vData.data.video_id) {
                if (vData.data.status === 1 || vData.data.convert_percent === 100) {
                    return vData.data.video_id;
                }
            }
        }
        throw new Error("Quá thời gian chờ Zalo OA chuyển đổi định dạng video.");
    }

    // Tạo bài viết dạng Video trên OA
    async createVideoArticle(videoArticleData) {
        const token = await this.ensureAccessToken();
        const payload = {
            type: "video",
            title: videoArticleData.title,
            description: videoArticleData.description,
            status: videoArticleData.status || "show",
            video_id: videoArticleData.video_id,
            avatar: videoArticleData.avatar,
            comment: videoArticleData.comment || "show"
        };

        const res = await fetch('https://openapi.zalo.me/v2.0/article/create', {
            method: 'POST',
            headers: {
                'access_token': token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        return await res.json();
    }

    // Cập nhật bài viết
    async updateArticle(articleData) {
        const token = await this.ensureAccessToken();
        return await this.request('openapi.zalo.me', '/v2.0/article/update', 'POST', {
            'access_token': token,
            'Content-Type': 'application/json'
        }, JSON.stringify(articleData));
    }

    // Helper thực hiện HTTPS Request
    request(hostname, path, method, headers, postData = null) {
        return new Promise((resolve, reject) => {
            const req = https.request({
                hostname,
                path,
                method,
                headers
            }, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    try {
                        resolve(JSON.parse(data));
                    } catch (e) {
                        resolve({ raw: data, status: res.statusCode });
                    }
                });
            });

            req.on('error', reject);
            if (postData) req.write(postData);
            req.end();
        });
    }
}

module.exports = new ZaloOaApi();
