import os
import logging
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
import requests

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes

# SMTP Configuration
SMTP_SERVER = 'us2.smtp.mailhostbox.com'
SMTP_PORT = 587
SMTP_USERNAME = 'info@alexsearscpa.com'
SMTP_PASSWORD = os.getenv('MAIL_PASSWORD')

# reCAPTCHA Configuration
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')

# Check for required environment variables
if not SMTP_PASSWORD:
    logging.error("MAIL_PASSWORD environment variable is not set")
if not os.getenv('GOOGLE_MAPS_API_KEY'):
    logging.error("GOOGLE_MAPS_API_KEY environment variable is not set")
if not RECAPTCHA_SECRET_KEY:
    logging.error("RECAPTCHA_SECRET_KEY environment variable is not set")

@app.route('/about-us')
def serve_about_us():
    return render_template('about-us.html')

@app.route('/contact')
def serve_contact():
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return render_template('contact.html', google_maps_api_key=google_maps_api_key)

@app.route('/services')
def serve_services():
    return render_template('services.html')

@app.route('/accounting-services')
def serve_accounting_services():
    return render_template('accounting-services.html')

@app.route('/tax-services')
def serve_tax_services():
    return render_template('tax-services.html')

@app.route('/consulting')
def serve_consulting():
    return render_template('consulting.html')

@app.route('/audit-and-assurance')
def serve_audit_and_assurance():
    return render_template('audit-and-assurance.html')

@app.route('/financial-planning')
def serve_financial_planning():
    return render_template('financial-planning.html')

@app.route('/business-advisory')
def serve_business_advisory():
    return render_template('business-advisory.html')

@app.route('/resources')
def serve_resources():
    return render_template('resources.html')

@app.route('/blog')
def serve_blog():
    return render_template('blog.html')

@app.route('/search-results')
def serve_search_results():
    return render_template('search-results.html')

@app.route('/pricing')
def serve_pricing():
    return render_template('pricing.html')

@app.route('/single-service')
def serve_single_service():
    return render_template('single-service.html')

@app.route('/single-blog-post')
def serve_single_blog_post():
    return render_template('single-blog-post.html')

@app.route('/grid-blog')
def serve_grid_blog():
    return render_template('grid-blog.html')

@app.route('/grid-gallery')
def serve_grid_gallery():
    return render_template('grid-gallery.html')

@app.route('/privacy-policy')
def serve_privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/')
def serve_index():
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return render_template('index.html', google_maps_api_key=google_maps_api_key)

@app.route('/contacts')
def serve_contacts():
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return render_template('contacts.html', google_maps_api_key=google_maps_api_key)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                                  'favicon.ico', mimetype='image/vnd.microsoft.icon')

def verify_recaptcha(recaptcha_response):
    logging.info(f"Verifying reCAPTCHA response: {recaptcha_response[:20]}...")  # Log first 20 chars for privacy
    secret_key = os.environ.get('RECAPTCHA_SECRET_KEY')
    if not secret_key:
        logging.error("RECAPTCHA_SECRET_KEY is not set in environment variables")
        return False
    logging.info(f"Using secret key: {secret_key[:5]}...")  # Log first 5 chars for security

    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        "secret": secret_key,
        "response": recaptcha_response
    }
    try:
        response = requests.post(verify_url, data=data)
        result = response.json()
        logging.info(f"reCAPTCHA verification result: {result}")
        if not result.get("success", False):
            logging.warning(f"reCAPTCHA verification failed. Error codes: {result.get('error-codes', [])}")
        return result.get("success", False)
    except Exception as e:
        logging.error(f"Error during reCAPTCHA verification: {str(e)}")
        return False

@app.route('/send_email', methods=['POST'])
@cross_origin()
def send_email():
    try:
        logging.info("Received form submission")
        logging.debug(f"Form data: {request.form}")
        
        # Verify reCAPTCHA
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not recaptcha_response:
            logging.warning("No reCAPTCHA response received")
            return jsonify({'error': 'Please complete the reCAPTCHA'}), 400
        
        if not verify_recaptcha(recaptcha_response):
            logging.warning("reCAPTCHA verification failed")
            return jsonify({'error': 'reCAPTCHA verification failed'}), 400

        logging.info("reCAPTCHA verification successful")

        # Rest of your email sending logic...
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        message = request.form.get('message', '')
        
        msg_body = f"Name: {first_name} {last_name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"

        msg = MIMEText(msg_body)
        msg['Subject'] = 'New Contact Form Submission'
        msg['From'] = SMTP_USERNAME
        msg['To'] = 'alexsearscpa@gmail.com'

        logging.debug(f"Email content: {msg_body}")
        logging.debug(f"SMTP server: {SMTP_SERVER}")
        logging.debug(f"SMTP port: {SMTP_PORT}")
        logging.debug(f"SMTP use TLS: True")
        logging.debug(f"SMTP username: {SMTP_USERNAME}")
        logging.debug(f"SMTP password: {SMTP_PASSWORD[:3]}***")  # Only log first 3 chars of password for security

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.set_debuglevel(1)  # Enable debug output
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(SMTP_USERNAME, ['alexsearscpa@gmail.com'], msg.as_string())

            logging.info("Email sent successfully")
            return jsonify({'message': 'Email sent successfully!'}), 200

        except smtplib.SMTPAuthenticationError as auth_error:
            logging.error(f"SMTP Authentication Error: {auth_error}")
            return jsonify({'error': 'SMTP Authentication Error'}), 500
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return jsonify({'error': 'Failed to send email'}), 500
    except Exception as e:
        logging.error(f"General Error in send_email route: {e}")
        return jsonify({'error': 'Failed to process the request'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)