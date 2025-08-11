import base64

decoded_session = base64.urlsafe_b64decode('eyJfcGVybWFuZW50Ijp0cnVlLCJhdXRoIjp0cnVlLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJ1c2VyIjoiVGVzdCJ9===')
print(decoded_session)

"""
Here is a reminder: secret key is just for signing, not encrypting the session, so you can read it without secret key.
Never ever store personal data in session! Or encrypt it.
Steps:
1. Open debug consol of your browser and go to Network or Storage->Cookies (Fitefox), Application->Cookies (Chrome) 
2. Login or register and then login to fill session with data
3. Copy the string first part (until first dot or of the session)
4. Paste and overwrite line 3 long string and add 3 equal char at the end ===
5. Run the code

Interesting article in this topic:
https://blog.paradoxis.nl/defeating-flasks-session-management-65706ba9d3ce
"""