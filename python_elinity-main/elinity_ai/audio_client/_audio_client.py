import os
import assemblyai as aai
from dotenv import load_dotenv
import boto3
from gtts import gTTS
import uuid 
import tempfile

load_dotenv()

class AudioTranscript: 
    """AudioTranscript class for transcribing audio to text using AssemblyAI."""
    def __init__(self, config=None, key=None): 
        self.key = key or os.environ.get("ASSEMBLYAI_API_KEY")

        if not self.key:
            raise RuntimeError(f"Assembly AI API key is required.") 
        aai.settings.api_key = self.key 
        
        if not config:
           self.config = config or aai.TranscriptionConfig(speech_model=aai.SpeechModel.best)
        self.client = aai.Transcriber(config=self.config) 
        
        self.s3_bucket = os.environ.get('AWS_BUCKET_NAME')
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        aws_region = os.environ.get('AWS_REGION')

        if not self.s3_bucket:
            raise ValueError("AWS_BUCKET_NAME environment variable is required")
        if not aws_access_key or not aws_secret_key:
            raise ValueError("AWS credentials are required (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)")
            
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
    def speech_to_text(self, audio):
        """Transcribe audio to text using AssemblyAI."""
        transcript = self.client.transcribe(audio)
        if transcript.status == 'error':
            raise RuntimeError(f"Couldn't transcribe audio: {transcript.error}") 
        return transcript.text
        
    def _save_to_s3(self, tts): 
        """Save the audio to S3."""
        filename = f"{uuid.uuid4()}.mp3"
        
        try:
            if not isinstance(self.s3_bucket, str):
                raise TypeError(f"Bucket name must be a string, got {type(self.s3_bucket)}")
            if not self.s3_bucket:
                raise ValueError("S3 bucket name is empty")
                
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"tts_{filename}")
            
            tts.save(temp_path)
            s3_key = f"tts/{filename}"
            
            self.s3_client.upload_file(
                Filename=temp_path,
                Bucket=self.s3_bucket,
                Key=s3_key,
                ExtraArgs={"ContentType": "audio/mpeg"}
            )
            
            url = f"https://{self.s3_bucket}.s3.amazonaws.com/{s3_key}"
            os.unlink(temp_path)
            
            return url
        except Exception as e:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
                
            raise RuntimeError(f"Failed to upload file to S3: {str(e)}")
            
    def text_to_speech(self, text): 
        """Convert text to speech and upload to S3."""
        try:
            tts = gTTS(text=text, lang='en')
            url = self._save_to_s3(tts)
            return url
        except Exception as e:
            raise RuntimeError(f"Failed to convert text to speech: {str(e)}")


transcriber = AudioTranscript()

 