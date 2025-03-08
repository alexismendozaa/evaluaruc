import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppComponent } from './app.component';
import { RucCheckerComponent } from './components/ruc-checker/ruc-checker.component';
import { TableComponent } from './components/table/table.component';
import { ChatbotComponent } from './components/chatbot/chatbot.component';  // 

@NgModule({
  declarations: [
    AppComponent,
    RucCheckerComponent,
    TableComponent,
    ChatbotComponent  // 
  ],
  imports: [
    BrowserModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
