import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  vus: 50,            // virtual users
  duration: '30s',    // test time
};

export default function () {
  http.get('http://localhost:8000/');
  sleep(0.1);
}
