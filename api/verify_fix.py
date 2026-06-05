from app.main import app

schema = app.openapi()
register = schema['paths']['/api/v1/auth/register']['post']

print("Register endpoint responses:")
for code, resp in register['responses'].items():
    print(f"  {code}: {resp.get('description', 'N/A')}")
