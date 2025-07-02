import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from schemas.cart_item import CartItemListResponse
from typing import Optional
from datetime import datetime
from core.config import settings

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER      # Will raise error if not in .env
        self.smtp_port = settings.SMTP_PORT          # Will raise error if not in .env  
        self.email_address = settings.EMAIL_ADDRESS  # Will raise error if not in .env
        self.email_password = settings.EMAIL_PASSWORD # Will raise error if not in .env
    
    def _generate_cart_html(self, cart_data: CartItemListResponse, user_name: str = "Customer") -> str:
        """Generate HTML content from CartItemListResponse"""
        
        # Start building HTML with your color palette
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your Shopping Cart Receipt</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .header {{
                    background: linear-gradient(135deg, #FFFFFF 30%, #f27012 20%, #ffc10e 20%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                    position: relative;
                }}
                .logo {{
                    width: 80px;
                    height: 80px;
                    margin: 0 auto 15px auto;
                    background: white;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                    overflow: hidden;
                }}
                .logo img {{
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                }}
                .container {{
                    background: white;
                    border-radius: 0 0 10px 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .summary {{
                    background: linear-gradient(45deg, #ffc10e, #f27012);
                    color: white;
                    padding: 20px;
                    border-bottom: 1px solid #e9ecef;
                }}
                .summary h2 {{
                    margin: 0 0 15px 0;
                    color: white;
                    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
                }}
                .summary-item {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 8px;
                    padding: 5px 0;
                    color: white;
                }}
                .summary-item.total {{
                    font-weight: bold;
                    font-size: 18px;
                    background: rgba(255, 255, 255, 0.2);
                    padding: 15px;
                    border-radius: 8px;
                    margin-top: 15px;
                    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
                }}
                .items {{
                    padding: 20px;
                }}
                .item {{
                    border-bottom: 1px solid #e9ecef;
                    padding: 15px 0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                .item:last-child {{
                    border-bottom: none;
                }}
                .item-details {{
                    flex: 1;
                }}
                .item-name {{
                    font-weight: bold;
                    font-size: 16px;
                    color: #206495;
                    margin-bottom: 5px;
                }}
                .item-name-ar {{
                    font-size: 14px;
                    color: #6c757d;
                    margin-bottom: 5px;
                    direction: rtl;
                }}
                .item-info {{
                    font-size: 14px;
                    color: #6c757d;
                }}
                .item-price {{
                    font-weight: bold;
                    font-size: 16px;
                    color: #f27012;
                    text-align: right;
                    min-width: 80px;
                }}
                .quantity-badge {{
                    background: #206495;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .footer {{
                    background: #206495;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    font-size: 14px;
                }}
                .footer a {{
                    color: #ffc10e;
                    text-decoration: none;
                    font-weight: bold;
                }}
                .footer a:hover {{
                    color: #f27012;
                }}
                .weight-info {{
                    background: #ffc10e;
                    color: #206495;
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-size: 12px;
                    margin-left: 5px;
                    font-weight: bold;
                }}
                .brand-accent {{
                    color: #f27012;
                    font-weight: bold;
                }}
                .price-highlight {{
                    background: linear-gradient(45deg, #ffc10e, #f27012);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    font-weight: bold;
                }}
                @media (max-width: 600px) {{
                    body {{
                        padding: 10px;
                    }}
                    .header {{
                        padding: 20px;
                    }}
                    .header h1 {{
                        font-size: 24px;
                    }}
                    .logo {{
                        width: 60px;
                        height: 60px;
                        font-size: 24px;
                    }}
                    .item {{
                        flex-direction: column;
                        align-items: flex-start;
                    }}
                    .item-price {{
                        align-self: flex-end;
                        margin-top: 10px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">
                    <img src="https://i.ibb.co/WvMCG6D9/DD811861-5-C31-48-F5-83-C1-155-A37065-ECD.png" alt="DuckyCart Logo" />
                </div>
                <h1>🛒 Your DuckyCart</h1>
                <p>Thank you for shopping with us!</p>
            </div>
            
            <div class="container">
                <div class="summary">
                    <h2>📊 Order Summary</h2>
                    <div class="summary-item">
                        <span>Total Items:</span>
                        <span><strong>{cart_data.item_count}</strong></span>
                    </div>
                    <div class="summary-item">
                        <span>Date:</span>
                        <span>{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</span>
                    </div>
                    <div class="summary-item total">
                        <span>🎯 Total Amount:</span>
                        <span>E£{cart_data.total_price:.2f}</span>
                    </div>
                </div>
                
                <div class="items">
                    <h2>🛍️ Items in Your Cart</h2>
        """
        
        # Add each item
        for item in cart_data.items:
            product = item.product
            if product:
                item_total = product.get('unit_price', 0) * item.quantity
                
                html_content += f"""
                    <div class="item">
                        <div class="item-details">
                            <div class="item-name">{product.get('description', 'Unknown Item')}</div>
                            <div class="item-name-ar">{product.get('description_ar', '')}</div>
                            <div class="item-info">
                                <span class="quantity-badge">Qty: {item.quantity}</span>
                                <span class="brand-accent">Unit Price: E£{product.get('unit_price', 0):.2f}</span>
                            </div>
                        </div>
                        <div class="item-price">E£{item_total:.2f}</div>
                    </div>
                """
        
        # Close HTML
        html_content += f"""
            </div>
            
                <div class="footer">
                    <p>🎉 Thank you for choosing <span style="color: #ffc10e; font-weight: bold;">DuckyCart</span>!</p>
                    <p>Questions? Contact us at <a href="mailto:duckycart@gmail.com">duckycart@gmail.com</a></p>
                    <p><small>This email was sent automatically. Please do not reply.</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def send_cart_email(
        self, 
        recipient_email: str, 
        cart_data: CartItemListResponse,
        user_name: str = "Customer",
        subject: Optional[str] = None
    ) -> bool:
        """
        Send cart data as HTML email to recipient
        
        Args:
            recipient_email: Email address to send to
            cart_data: CartItemListResponse object containing cart items
            user_name: Name of the customer
            subject: Custom email subject (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        
        if not subject:
            subject = f"🦆 Your DuckyCart Receipt - {cart_data.item_count} items (E£{cart_data.total_price:.2f})"
        
        # Generate HTML content
        html_body = self._generate_cart_html(cart_data, user_name)
        
        # Create plain text version
        plain_text = f"""
        🦆 DuckyCart Receipt
        
        Dear {user_name},
        
        Thank you for shopping with DuckyCart!
        
        Your Cart Summary:
        - Total Items: {cart_data.item_count}
        - Total Amount: E£{cart_data.total_price:.2f}
        - Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        
        Items:
        """
        
        for item in cart_data.items:
            if item.product:
                item_total = item.product.get('unit_price', 0) * item.quantity  # ✅ Fixed: item.product instead of product
                plain_text += f"- {item.product.get('description', 'Unknown Item')} (Qty: {item.quantity}) - E£{item_total:.2f}\n"
        
        plain_text += f"""

        Questions? Contact us at duckycart@gmail.com

        Best regards,
        🦆 DuckyCart Team
        """
        
        # Construct the email
        message = MIMEMultipart('alternative')
        message['From'] = self.email_address
        message['To'] = recipient_email
        message['Subject'] = subject
        
        # Attach both plain text and HTML versions
        text_part = MIMEText(plain_text, 'plain')
        html_part = MIMEText(html_body, 'html')
        
        message.attach(text_part)
        message.attach(html_part)
        
        try:
            # Connect to SMTP server and send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Use TLS
            server.login(self.email_address, self.email_password)
            server.send_message(message)
            server.quit()
            
            print(f"✅ Cart email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send cart email to {recipient_email}: {e}")
            return False

# Create a singleton instance
email_service = EmailService()

def send_cart_receipt_email(recipient_email: str, cart_data: CartItemListResponse, user_name: str = "Customer") -> bool:
    """
    Convenience function to send cart receipt email
    
    Args:
        recipient_email: Email address to send to
        cart_data: CartItemListResponse object containing cart items
        user_name: Name of the customer
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    return email_service.send_cart_email(recipient_email, cart_data, user_name)