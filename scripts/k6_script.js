import http from 'k6/http';
import { check } from 'k6';

const BASE_URL = 'http://homepage_service:80'; // Update with actual container name and port

export default function () {
  // Run the query 10 times
  for (let i = 0; i < 10; i++) {
    // Test the /hello endpoint
    let response = http.get(`${BASE_URL}/hello`);
    
    // Check if the response status is 200
    check(response, { 'status is 200': (r) => r.status === 200 });
  }
}

