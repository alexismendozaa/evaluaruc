import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { PredictorService } from '../../services/predictor.service';
import { ChatbotService } from '../../services/chatbot/chatbot.service';

@Component({
  selector: 'app-ruc-checker',
  standalone: true,
  templateUrl: './ruc-checker.component.html',
  styleUrls: ['./ruc-checker.component.css'],
  imports: [FormsModule, CommonModule]
})
export class RucCheckerComponent {
  ruc: string = '';
  error: string = '';
  resultado: any = null;

  constructor(private predictorService: PredictorService, private chatbotService: ChatbotService) {}

  buscarRUC() {
    if (!this.ruc) {
      this.error = "⚠️ Debes ingresar un RUC válido.";
      return;
    }
    this.error = ""; // Limpiar errores previos

    this.predictorService.consultarRUC(this.ruc).subscribe({
      next: (data) => {
        this.resultado = data;
        console.log("✅ Respuesta del servidor:", data);

        if (!data.error) {
          // Activar el chatbot automáticamente con los datos obtenidos
          this.chatbotService.activateChatbot(this.ruc, data.razon_social, data.riesgo);
        }
      },
      error: (err) => {
        console.error("❌ Error al consultar el RUC:", err);
        this.error = "⚠️ No se pudo obtener datos del servidor.";
      }
    });
  }

  nuevaConsulta() {
    // Limpiar datos
    this.resultado = null;
    this.ruc = '';
    this.error = '';

    // Reiniciar el historial del chatbot
    this.chatbotService.clearChatHistory();
  }

  formatDate(date: string): string {
    if (date === "Sinreinicio" || date === "Vigente") {
      return date;
    }
    const formattedDate = new Date(date);
    return formattedDate.toLocaleString();
  }
}
