import base64

def convert_to_base64(file_path):
    with open(file_path, 'rb') as img:
        image_data = img.read()
        base64_encoded_image = base64.b64encode(image_data)
        base64_string = base64_encoded_image.decode('utf-8')
        return base64_string