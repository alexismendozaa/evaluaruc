import { Component, EventEmitter, Output, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatbotService } from '../../services/chatbot/chatbot.service';

@Component({
  selector: 'app-chatbot',
  standalone: true,
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css'],
  imports: [CommonModule, FormsModule]
})
export class ChatbotComponent implements OnInit {
  @Output() nuevaConsultaEvent = new EventEmitter<void>(); // ✅ Evento para comunicar con el componente padre

  isOpen = false;
  userMessage = '';
  messages: { role: string, text: string }[] = [];
  ruc: string = '';
  riskLevel: string = '';
  isNewQuery = true; // ✅ Controla si es una nueva consulta

  constructor(private chatbotService: ChatbotService) {}

  ngOnInit() {
    this.chatbotService.chatbotTrigger.subscribe(data => {
      this.isOpen = true;
      
      // ✅ Si el RUC cambia, limpiar historial
      if (this.ruc !== data.ruc) {
        this.resetChat();
      }

      this.ruc = data.ruc;
      this.riskLevel = data.risk;

      // ✅ Mensaje inicial solo si es una nueva consulta
      if (this.isNewQuery) {
        this.messages.push({ 
          role: 'bot', 
          text: this.formatBotResponse(`👋 ¡Hola! ${data.name}, tu nivel de riesgo es: **${data.risk}**.\n\n¿Te gustaría recibir consejos fiscales o tienes otra consulta?`)
        });
        this.isNewQuery = false;
      }
    });
  }

  toggleChatbot() {
    this.isOpen = !this.isOpen;
  }

  sendMessage() {
    if (this.userMessage.trim() === '') return;

    const userText = this.userMessage;
    this.messages.push({ role: 'user', text: userText });
    this.userMessage = '';

    // ✅ Enviar mensaje sin borrar historial en consultas continuas
    this.chatbotService.getChatbotResponse(this.ruc, this.riskLevel, userText).subscribe(response => {
      this.messages.push({ role: 'bot', text: this.formatBotResponse(response.response) });
    });
  }

  // ✅ Función para borrar el chat cuando se hace una nueva consulta
  resetChat() {
    this.messages = [];
    this.isNewQuery = true;
    this.nuevaConsultaEvent.emit(); // ✅ Dispara el evento al componente padre
  }

  // ✅ Formateo de la respuesta del bot para mejorar la visualización
  formatBotResponse(response: string): string {
    return response
      .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>') // Negritas
      .replace(/\n/g, '<br>') // Saltos de línea
      .replace(/\* (.*?)\n/g, '<li>$1</li>'); // Listas con viñetas
  }
}
