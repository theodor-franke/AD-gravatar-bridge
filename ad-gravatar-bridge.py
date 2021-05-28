import ldap
import io
import hashlib

# Your LDAP server
SERVER = 'ldap://example.com'

# A service-user for accessing LDAP
USERNAME = 'cn=servldap,ou=ServiceUser,dc=example,dc=com'
PASSWORD = 'S3CR3T'

# A query for filtering the LDAP
BASE_DN = 'OU=Users,DC=example,DC=com'

# Avatar Location
AVATAR_LOCATION = '/var/www/avatars'


l = ldap.initialize(SERVER)
l.simple_bind_s(USERNAME, PASSWORD)

# Get all objects which have a thumbnailPhoto
ldap_result_id = l.search(BASE_DN, ldap.SCOPE_SUBTREE, 'thumbnailPhoto=*', None)

# Loop over all the results
while 1:
    result_type, result_data = l.result(ldap_result_id, 0)
    if (result_data == []):
        break
    else:
        if result_type == ldap.RES_SEARCH_ENTRY:
            try:
                # Get the image
                raw_image = result_data[0][1]['thumbnailPhoto'][0]
                # Get the Email and make it lower case
                mail = result_data[0][1]['mail'][0].decode("utf-8").lower()
                # hash the email with md5 and get the has represented in utf-8 back
                hash = hashlib.md5(mail.encode('utf-8')).hexdigest()
                # save the image to a file and give it the name of the jpeg
                file = open('{}/{}.jpeg'.format(AVATAR_LOCATION, hash), 'wb')
                file.write(raw_image)
                file.close()

            except:
                print("Error with: {}".format(result_data[0][1]['cn'][0]))
