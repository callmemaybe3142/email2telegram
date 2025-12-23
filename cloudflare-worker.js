export default {
    async email(message, env, ctx) {
        // Configuration - Replace with your actual webhook URL
        const WEBHOOK_URL = "https://bath-ali-carries-athletes.trycloudflare.com/webhook/email";

        try {
            console.log("📧 Email received at Cloudflare Worker");
            console.log("From:", message.from);
            console.log("To:", message.to);
            console.log("Subject:", message.headers.get("subject"));

            // Get the raw email content as ArrayBuffer
            const rawEmail = await streamToArrayBuffer(message.raw);

            // Forward the raw email to FastAPI webhook
            const response = await fetch(WEBHOOK_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "message/rfc822",
                    "X-Cloudflare-Worker": "true",
                },
                body: rawEmail,
            });

            if (response.ok) {
                console.log("✅ Email forwarded successfully to webhook");
                const result = await response.json();
                console.log("Response:", result);
            } else {
                console.error("❌ Failed to forward email:", response.status, response.statusText);
                const errorText = await response.text();
                console.error("Error details:", errorText);
            }

        } catch (error) {
            console.error("❌ Error processing email:", error.message);
            console.error("Stack:", error.stack);
        }
    },
};

/**
 * Helper function to convert ReadableStream to ArrayBuffer
 */
async function streamToArrayBuffer(stream) {
    const reader = stream.getReader();
    const chunks = [];

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        chunks.push(value);
    }

    // Calculate total length
    const totalLength = chunks.reduce((acc, chunk) => acc + chunk.length, 0);

    // Combine all chunks into a single Uint8Array
    const result = new Uint8Array(totalLength);
    let offset = 0;
    for (const chunk of chunks) {
        result.set(chunk, offset);
        offset += chunk.length;
    }

    return result.buffer;
}
