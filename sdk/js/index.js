const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

class Client {
  constructor(baseUrl = "http://localhost:8000/v1") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async tts(text, options = {}) {
    try {
      const response = await axios.post(`${this.baseUrl}/tts`, { text, ...options });
      return response.data;
    } catch (error) {
      console.error("TTS Error:", error);
      throw error;
    }
  }

  async render({ imagePath, text, voiceProfileId }) {
    try {
      const form = new FormData();
      form.append('image', fs.createReadStream(imagePath));
      form.append('text', text);
      form.append('consent_confirmed', 'true');
      if (voiceProfileId) form.append('voice_profile_id', voiceProfileId);

      const response = await axios.post(`${this.baseUrl}/render`, form, {
        headers: {
          ...form.getHeaders()
        }
      });
      return response.data;
    } catch (error) {
      console.error("Render Error:", error);
      throw error;
    }
  }
}

module.exports = Client;
