pyinstaller mcl.spec

openssl req -x509 -newkey rsa:4096 -keyout clave.key -out certificado.pem -days 1095 -nodes
openssl pkcs12 -export -out certificado.pfx -inkey clave.key -in certificado.pem
Country Name (2 letter code) [AU]:AR
State or Province Name (full name) [Some-State]:Buenos Aires
Locality Name (eg, city) []:Ciudad de Buenos Aires
Organization Name (eg, company) [Internet Widgits Pty Ltd]:Minecito LLA
Organizational Unit Name (eg, section) []:Minecito
Common Name (e.g. server FQDN or YOUR name) []:Lucas Goldstein
Email Address []:mc-contact@gmail.com

osslsigncode sign -pkcs12 certificado.pfx -h sha256 -n "MinecitoLauncher" -ts http://timestamp.digicert.com -in dist/MinecitoLauncher.exe -out dist/MinecitoLauncher_Signed.exe -nolegacy -pass minecito