import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
    stages: [
        { duration: '10s', target: 100 }, // Ramp up to 100 users over 5 minutes
        { duration: '20s', target: 100 }, // Stay at 100 users for 10 minutes
        { duration: '10s', target: 0 }, // Ramp down to 0 users over 5 minutes
    ],
    thresholds: {
        http_req_duration: ['p(99)<10']
    }
};

export default function () {
    let r = http.get('http://database_service:80/count');
    check(r, {  
        'is status 200': (r) => r.status === 200,
    });
    sleep(1);
}
