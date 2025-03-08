import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ChatbotService {
  private apiUrl = 'http://127.0.0.1:5000/chatbot';
  chatbotTrigger = new Subject<{ ruc: string, name: string, risk: string }>();

  constructor(private http: HttpClient) {}

  getChatbotResponse(ruc: string, riskLevel: string, userMessage: string): Observable<any> {
    return this.http.post<any>(this.apiUrl, { 
      ruc, 
      risk_level: riskLevel, 
      user_message: userMessage  // ✅ Enviamos el mensaje del usuario y el nivel de riesgo
    });
  }

  activateChatbot(ruc: string, name: string, risk: string) {
    this.chatbotTrigger.next({ ruc, name, risk });
  }

  clearChatHistory() {
    this.chatbotTrigger.next({ ruc: '', name: '', risk: '' }); // 🔥 Borra el historial sin afectar el mensaje inicial en la próxima consulta
  }
  
}
