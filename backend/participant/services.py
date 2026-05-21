import uuid
import qrcode
from io import BytesIO
from django.core.files import File

def generate_team_qr_code(team):
    """
    Generates and saves a QR code for the team if one does not exist.
    Contains only the string representation of qr_token.
    """
    # Generate qr_token UUID if not present
    if not team.qr_token:
        team.qr_token = uuid.uuid4()
        team.save(update_fields=['qr_token'])
        
    # Generate qr_code image if not present
    if not team.qr_code:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(str(team.qr_token))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f"team_{team.id}_qr.png"
        team.qr_code.save(filename, File(buffer), save=False)
        team.save(update_fields=['qr_code'])
