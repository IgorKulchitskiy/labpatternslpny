Лабки з патернів :)

For running lab2 branch you need to pip install sqlalchemy

For this backend API authorization you also need JWT package:

pip install PyJWT

Login endpoint:

POST /api/login
{
	"email": "igor@gmail.com",
	"password": "1111"
}

Terminal check example (shows message + status 200):

curl -i -X POST http://127.0.0.1:5000/api/login -H "Content-Type: application/json" -d "{\"email\":\"igor@gmail.com\",\"password\":\"1111\"}"

Separate endpoint for terminal status check:

curl -i -X POST http://127.0.0.1:5000/api/login-status -H "Content-Type: application/json" -d "{\"email\":\"igor@gmail.com\",\"password\":\"1111\"}"

Use returned access_token in header:

Authorization: Bearer <access_token>

Browser flow:
- Open /login
- Use email: igor@gmail.com
- Use password: 1111
- After successful login JWT token is saved in HttpOnly cookie, popup is shown, and pages with data become available

Protected endpoints:
- GET /api/scenarios
- GET /api/scenarios/<id>
- POST /api/scenarios
- PUT /api/scenarios/<id>
- DELETE /api/scenarios/<id>