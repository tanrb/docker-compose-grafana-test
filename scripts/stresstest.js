import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
    stages: [
        { duration: '1m', target: 50 }, // Ramp up to 50 users over 1 minute
        { duration: '1m', target: 50 }, // Stay at 50 users for 1 minute
        { duration: '1m', target: 200 }, // Spike to 200 users over 1 minute
        { duration: '3m', target: 200 }, // Stay at 200 users for 3 minutes
        { duration: '1m', target: 50 }, // Drop back to 50 users over 1 minute
        { duration: '1m', target: 0 }, // Ramp down to 0 users over 1 minute
    ],
};

export default function () {
    let r = http.get('http://database_service:80/count');
    check(r, {
        'is status 200': (r) => r.status === 200,
    });
    sleep(1);
}
