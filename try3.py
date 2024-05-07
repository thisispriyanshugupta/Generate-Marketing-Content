# !pip install transformers
# !pip install flask

from flask import Flask, request, jsonify
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import re

class SocialMediaPostGenerator:

    def __init__(self):
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
        self.model = GPT2LMHeadModel.from_pretrained("gpt2")
    
    def generate_post(self, topic, platform, emotion=None, length=100):
        # Construct the prompt based on the input parameters
        prompt = f"As a {emotion} {platform} user, I want to share some thoughts on {topic}. I am looking for a {length} post that covers the key aspects of {topic}, its impact on various industries, and the future possibilities it holds. The post should be engaging and informative, sparking curiosity and conversation among my network. Use appropriate hashtags."
        if emotion:
            prompt += f" The tone should be {emotion}."

        # Tokenize the prompt
        inputs = self.tokenizer(prompt, return_tensors="pt")

        # Generate the content using the GPT-2 model with attention mask and pad token id
        outputs = self.model.generate(input_ids=inputs.input_ids, attention_mask=inputs.attention_mask, max_length=length, num_return_sequences=1, pad_token_id=self.tokenizer.eos_token_id, do_sample=True, temperature=0.7)

        # Decode the generated content
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Post-processing: Remove any URLs or irrelevant information from the generated text
        text = re.sub(r'http\S+|www.\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'<.*?>', '', text)  # Remove HTML tags

        return {"text": text}

app = Flask(__name__)
generator = SocialMediaPostGenerator()

@app.route('/generate', methods=['POST'])
def generate_post():
    data = request.get_json()
    topic = data.get('topic')
    platform = data.get('format')
    emotion = data.get('emotion')
    length = data.get('length', 100)

    if not topic or not platform:
        return jsonify({'error': 'Both topic and format are required'}), 400

    output = generator.generate_post(topic, platform, emotion, length)
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)
