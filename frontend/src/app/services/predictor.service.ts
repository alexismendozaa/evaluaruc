import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PredictorService {
  private apiUrl = 'http://localhost:5000/predict';  // ✅ Confirma que es la correcta

  constructor(private http: HttpClient) {}

  consultarRUC(ruc: string): Observable<any> {
    return this.http.post<any>(this.apiUrl, { ruc });
  }
}
