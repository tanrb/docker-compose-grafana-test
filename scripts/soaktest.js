import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
    stages: [
        { duration: '1h', target: 200 }, // Ramp up to 200 users over 1 hour
        { duration: '6h', target: 200 }, // Stay at 200 users for 6 hours
        { duration: '1h', target: 0 }, // Ramp down to 0 users over 1 hour
    ],
};

export default function () {
    let r = http.get('http://database_service:80/count');
    check(r, {
        'is status 200': (r) => r.status === 200,
    });
    sleep(1);
}
