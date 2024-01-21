import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
    stages: [
        { duration: '2m', target: 100 }, // Ramp up to 100 users over 2 minutes
        { duration: '5m', target: 100 }, // Stay at 100 users for 5 minutes
        { duration: '2m', target: 200 }, // Increase to 200 users over 2 minutes
        { duration: '5m', target: 200 }, // Stay at 200 users for 5 minutes
        { duration: '2m', target: 300 }, // Increase to 300 users over 2 minutes
        { duration: '5m', target: 300 }, // Stay at 300 users for 5 minutes
        { duration: '2m', target: 0 }, // Ramp down to 0 users over 2 minutes
    ],
};

export default function () {
    let r = http.get('http://database_service:80/count');
    check(r, {
        'is status 200': (r) => r.status === 200,
    });
    sleep(1);
}
