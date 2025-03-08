import { Component } from '@angular/core';
import { RucCheckerComponent } from './components/ruc-checker/ruc-checker.component';
import { TableComponent } from './components/table/table.component';
import { ChatbotComponent } from './components/chatbot/chatbot.component';  // ✅ Importar chatbot

@Component({
  selector: 'app-root',
  standalone: true,
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  imports: [RucCheckerComponent, TableComponent, ChatbotComponent]  // ✅ Agregar chatbot aquí
})
export class AppComponent {
  title = 'frontend';
}
