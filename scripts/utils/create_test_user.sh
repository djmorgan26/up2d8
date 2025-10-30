#!/bin/bash

echo "Creating test user account..."
curl -s -X POST http://localhost:8000/api/v1/auth/signup -H "Content-Type: application/json" -d '{"email":"davidjmorgan26@gmail.com","password":"password12345","full_name":"David Morgan"}' | python3 -m json.tool
