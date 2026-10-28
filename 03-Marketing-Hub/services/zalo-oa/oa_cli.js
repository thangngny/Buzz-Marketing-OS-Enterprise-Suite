const oaApi = require('./oa_api');

function getArg(flag) {
    const idx = process.argv.indexOf(flag);
    return idx !== -1 && process.argv[idx + 1] ? process.argv[idx + 1] : null;
}

async function main() {
    const cmd = process.argv[2];

    switch (cmd) {
        case "status": {
            try {
                const config = oaApi.config;
                const hasCreds = Boolean(config.app_id && config.secret_key && (config.access_token || config.refresh_token));
                console.log(JSON.stringify({
                    status: hasCreds ? "CONFIGURED" : "PENDING_CREDENTIALS",
                    app_id: config.app_id ? `***${config.app_id.slice(-4)}` : "Chưa có",
                    oa_id: config.oa_id || "Chưa có",
                    has_access_token: Boolean(config.access_token),
                    has_refresh_token: Boolean(config.refresh_token),
                    token_expires_at: config.expires_at ? new Date(config.expires_at).toLocaleString('vi-VN') : "Chưa có",
                    config_path: "C:\\Users\\Admin\\.buzz\\credentials\\zalo_oa_config.json"
                }, null, 2));
            } catch (err) {
                console.error("Lỗi kiểm tra status:", err.message);
                process.exit(1);
            }
            break;
        }

        case "send": {
            const to = getArg("--to") || getArg("-u");
            const message = getArg("--message") || getArg("-m");
            const quoteId = getArg("--quote");
            if (!to || !message) {
                console.error("Thiếu tham số: --to <user_id> --message <nội_dung>");
                process.exit(1);
            }
            try {
                const res = await oaApi.sendTextMessage(to, message, quoteId);
                console.log(JSON.stringify({ success: res.error === 0, result: res }, null, 2));
            } catch (err) {
                console.error(JSON.stringify({ success: false, error: err.message }, null, 2));
                process.exit(1);
            }
            break;
        }

        case "send-image": {
            const to = getArg("--to") || getArg("-u");
            const imageUrl = getArg("--image") || getArg("--url");
            const text = getArg("--message") || getArg("-m") || "";
            if (!to || !imageUrl) {
                console.error("Thiếu tham số: --to <user_id> --image <image_url>");
                process.exit(1);
            }
            try {
                const res = await oaApi.sendImageMessage(to, imageUrl, text);
                console.log(JSON.stringify({ success: res.error === 0, result: res }, null, 2));
            } catch (err) {
                console.error(JSON.stringify({ success: false, error: err.message }, null, 2));
                process.exit(1);
            }
            break;
        }

        case "send-zns": {
            const phone = getArg("--phone") || getArg("-p");
            const templateId = getArg("--template") || getArg("-t");
            const dataStr = getArg("--data") || "{}";
            if (!phone || !templateId) {
                console.error("Thiếu tham số: --phone <số_điện_thoại> --template <template_id> [--data '{\"key\":\"value\"}']");
                process.exit(1);
            }
            try {
                const templateData = JSON.parse(dataStr);
                const res = await oaApi.sendZns(phone, templateId, templateData);
                console.log(JSON.stringify({ success: res.error === 0, result: res }, null, 2));
            } catch (err) {
                console.error(JSON.stringify({ success: false, error: err.message }, null, 2));
                process.exit(1);
            }
            break;
        }

        case "profile": {
            const user = getArg("--user") || getArg("-u");
            if (!user) {
                console.error("Thiếu tham số: --user <user_id>");
                process.exit(1);
            }
            try {
                const res = await oaApi.getProfile(user);
                console.log(JSON.stringify(res, null, 2));
            } catch (err) {
                console.error("Lỗi lấy thông tin:", err.message);
                process.exit(1);
            }
            break;
        }

        case "followers": {
            const count = parseInt(getArg("--count") || "20", 10);
            try {
                const res = await oaApi.getFollowers(0, count);
                console.log(JSON.stringify(res, null, 2));
            } catch (err) {
                console.error("Lỗi lấy followers:", err.message);
                process.exit(1);
            }
            break;
        }

        case "info": {
            try {
                const res = await oaApi.getOaInfo();
                console.log(JSON.stringify(res, null, 2));
            } catch (err) {
                console.error("Lỗi lấy thông tin OA:", err.message);
                process.exit(1);
            }
            break;
        }

        case "articles": {
            const offset = parseInt(getArg("--offset") || "0", 10);
            const limit = parseInt(getArg("--limit") || "10", 10);
            const type = getArg("--type") || "normal";
            try {
                const res = await oaApi.getArticles(offset, limit, type);
                console.log(JSON.stringify(res, null, 2));
            } catch (err) {
                console.error("Lỗi lấy danh sách bài viết:", err.message);
                process.exit(1);
            }
            break;
        }

        case "article-detail": {
            const id = getArg("--id");
            if (!id) {
                console.error("Thiếu tham số: --id <article_id>");
                process.exit(1);
            }
            try {
                const res = await oaApi.getArticleDetail(id);
                console.log(JSON.stringify(res, null, 2));
            } catch (err) {
                console.error("Lỗi lấy chi tiết bài viết:", err.message);
                process.exit(1);
            }
            break;
        }

        case "article-create": {
            const jsonFile = getArg("--json-file") || getArg("-f");
            const fs = require('fs');
            let articlePayload = null;

            if (jsonFile) {
                try {
                    articlePayload = JSON.parse(fs.readFileSync(jsonFile, 'utf8'));
                } catch (e) {
                    console.error("Lỗi đọc file JSON bài viết:", e.message);
                    process.exit(1);
                }
            } else {
                const title = getArg("--title") || getArg("-t");
                const coverUrl = getArg("--cover") || getArg("-c");
                const desc = getArg("--desc") || getArg("-d");
                const author = getArg("--author") || "Minh Vân Logistics";
                const status = getArg("--status") || "show";
                const comment = getArg("--comment") || "show";
                const bodyFile = getArg("--body-file");
                const content = getArg("--content") || getArg("-m");

                if (!title || !coverUrl || !desc) {
                    console.error("Thiếu tham số bắt buộc: --title <tiêu_đề> --cover <url_ảnh> --desc <mô_tả>");
                    console.error("Nội dung có thể truyền qua: --json-file <path>, hoặc --body-file <path>, hoặc --content <text>");
                    process.exit(1);
                }

                let body = [];
                if (bodyFile && fs.existsSync(bodyFile)) {
                    const raw = fs.readFileSync(bodyFile, 'utf8');
                    try {
                        const parsed = JSON.parse(raw);
                        body = Array.isArray(parsed) ? parsed : (parsed.body || []);
                    } catch {
                        // Plain text / markdown lines
                        body = raw.split(/\r?\n\r?\n/).map(p => p.trim()).filter(Boolean).map(p => ({
                            type: "text",
                            content: p.startsWith("<p>") ? p : `<p>${p}</p>`
                        }));
                    }
                } else if (content) {
                    body = content.split(/\r?\n\r?\n/).map(p => p.trim()).filter(Boolean).map(p => ({
                        type: "text",
                        content: p.startsWith("<p>") ? p : `<p>${p}</p>`
                    }));
                }

                articlePayload = {
                    type: "normal",
                    title,
                    author,
                    cover: {
                        cover_type: "photo",
                        photo_url: coverUrl,
                        status: "show"
                    },
                    description: desc,
                    body,
                    status,
                    comment
                };
            }

            try {
                const res = await oaApi.createArticle(articlePayload);
                console.log(JSON.stringify({ success: res.error === 0, result: res }, null, 2));
            } catch (err) {
                console.error(JSON.stringify({ success: false, error: err.message }, null, 2));
                process.exit(1);
            }
            break;
        }

        case "video-upload": {
            const videoPath = getArg("--file") || getArg("-f");
            if (!videoPath) {
                console.error("Thiếu tham số: --file <path_to_video.mp4>");
                process.exit(1);
            }
            try {
                const videoId = await oaApi.uploadVideo(videoPath);
                console.log(JSON.stringify({ success: true, video_id: videoId }, null, 2));
            } catch (err) {
                console.error(JSON.stringify({ success: false, error: err.message }, null, 2));
                process.exit(1);
            }
            break;
        }

        case "video-article-create": {
            const videoId = getArg("--video-id") || getArg("-v");
            const videoFile = getArg("--file");
            const title = getArg("--title") || getArg("-t");
            const desc = getArg("--desc") || getArg("-d") || title;
            const avatar = getArg("--avatar") || getArg("--cover") || "https://zalo-article-photo.zadn.vn/331f575f9b03725d2b12#435204888";
            const status = getArg("--status") || "show";

            if (!title) {
                console.error("Thiếu tham số: --title <tiêu_đề> [--video-id <id> hoặc --file <path>]");
                process.exit(1);
            }

            try {
                let finalVideoId = videoId;
                if (!finalVideoId && videoFile) {
                    finalVideoId = await oaApi.uploadVideo(videoFile);
                }
                if (!finalVideoId) {
                    console.error("Không có video_id hoặc file video hợp lệ.");
                    process.exit(1);
                }

                const res = await oaApi.createVideoArticle({
                    title,
                    description: desc,
                    video_id: finalVideoId,
                    avatar,
                    status
                });
                console.log(JSON.stringify({ success: res.error === 0, result: res, video_id: finalVideoId }, null, 2));
            } catch (err) {
                console.error(JSON.stringify({ success: false, error: err.message }, null, 2));
                process.exit(1);
            }
            break;
        }

        default:
            console.log(`
Zalo OA CLI Controller (OpenAPI v3.0 / Article v2.0)
Cách dùng:
  zalo-oa-control status
  zalo-oa-control info
  zalo-oa-control articles [--offset 0] [--limit 10]
  zalo-oa-control article-detail --id <article_id>
  zalo-oa-control article-create --json-file <path_to_json>
  zalo-oa-control article-create --title "<tiêu_đề>" --cover "<url_ảnh>" --desc "<mô_tả>" --body-file <file_nội_dung> [--status show|hide]
  zalo-oa-control send --to <user_id> --message "Nội dung phản hồi"
  zalo-oa-control send-image --to <user_id> --image "<url_ảnh>" --message "Lời nhắn"
  zalo-oa-control send-zns --phone <098xxxxxxx> --template <template_id> --data '{"name":"Nam"}'
  zalo-oa-control profile --user <user_id>
  zalo-oa-control followers --count 20
            `);
            break;
    }
}

main();
