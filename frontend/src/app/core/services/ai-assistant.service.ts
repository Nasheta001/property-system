import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { AIConversation, AIMessage, StartConversationResponse } from '../models/ai-assistant.model';
import { PaginatedResponse } from '../models/property.model';

@Injectable({ providedIn: 'root' })
export class AiAssistantService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/ai/conversations`;

  listConversations(): Observable<PaginatedResponse<AIConversation>> {
    return this.http.get<PaginatedResponse<AIConversation>>(`${this.baseUrl}/`, { params: { page_size: 50 } });
  }

  startConversation(question: string): Observable<StartConversationResponse> {
    return this.http.post<StartConversationResponse>(`${this.baseUrl}/start/`, { question });
  }

  getMessages(conversationId: string): Observable<AIMessage[]> {
    return this.http.get<AIMessage[]>(`${this.baseUrl}/${conversationId}/messages/`);
  }

  askFollowUp(conversationId: string, question: string): Observable<AIMessage> {
    return this.http.post<AIMessage>(`${this.baseUrl}/${conversationId}/messages/`, { question });
  }
}
