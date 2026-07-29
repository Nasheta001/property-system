import { Component, ElementRef, OnInit, ViewChild, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';

import { AIConversation, AIMessage } from '../../core/models/ai-assistant.model';
import { AiAssistantService } from '../../core/services/ai-assistant.service';

interface SuggestedQuestion {
  label: string;
  question: string;
}

@Component({
  selector: 'app-assistant-page',
  imports: [FormsModule, MatButtonModule, MatIconModule, MatProgressSpinnerModule],
  templateUrl: './assistant-page.component.html',
  styleUrl: './assistant-page.component.scss',
})
export class AssistantPageComponent implements OnInit {
  private readonly aiAssistantService = inject(AiAssistantService);
  private readonly snackBar = inject(MatSnackBar);

  @ViewChild('transcriptEnd') private transcriptEnd?: ElementRef<HTMLDivElement>;

  protected readonly isLoadingConversations = signal(true);
  protected readonly isSending = signal(false);
  protected readonly conversations = signal<AIConversation[]>([]);
  protected readonly activeConversationId = signal<string | null>(null);
  protected readonly messages = signal<AIMessage[]>([]);
  protected draft = '';

  protected readonly suggestedQuestions: SuggestedQuestion[] = [
    { label: 'Overdue rent', question: 'Do we have any overdue rent this month?' },
    { label: 'Occupancy', question: "What's our current occupancy?" },
    { label: 'Open maintenance', question: 'What maintenance requests are still open?' },
    { label: 'Leases expiring', question: 'Which leases are ending soon?' },
  ];

  ngOnInit(): void {
    this.loadConversations();
  }

  private loadConversations(): void {
    this.isLoadingConversations.set(true);
    this.aiAssistantService.listConversations().subscribe({
      next: (response) => {
        this.conversations.set(response.results);
        this.isLoadingConversations.set(false);
      },
      error: () => this.isLoadingConversations.set(false),
    });
  }

  openConversation(conversation: AIConversation): void {
    this.activeConversationId.set(conversation.id);
    this.aiAssistantService.getMessages(conversation.id).subscribe({
      next: (messages) => {
        this.messages.set(messages);
        this.scrollToEnd();
      },
    });
  }

  newConversation(): void {
    this.activeConversationId.set(null);
    this.messages.set([]);
    this.draft = '';
  }

  ask(question?: string): void {
    const text = (question ?? this.draft).trim();
    if (!text || this.isSending()) return;

    this.isSending.set(true);
    const conversationId = this.activeConversationId();

    if (conversationId) {
      this.messages.update((list) => [...list, this.optimisticUserMessage(text)]);
      this.draft = '';
      this.scrollToEnd();

      this.aiAssistantService.askFollowUp(conversationId, text).subscribe({
        next: (message) => {
          this.messages.update((list) => [...list, message]);
          this.isSending.set(false);
          this.scrollToEnd();
        },
        error: (err) => this.handleError(err),
      });
    } else {
      this.messages.set([this.optimisticUserMessage(text)]);
      this.draft = '';
      this.scrollToEnd();

      this.aiAssistantService.startConversation(text).subscribe({
        next: (response) => {
          this.activeConversationId.set(response.conversation.id);
          this.messages.update((list) => [...list, response.message]);
          this.conversations.update((list) => [response.conversation, ...list]);
          this.isSending.set(false);
          this.scrollToEnd();
        },
        error: (err) => this.handleError(err),
      });
    }
  }

  onEnter(event: Event): void {
    const keyboardEvent = event as KeyboardEvent;
    if (keyboardEvent.shiftKey) return;
    event.preventDefault();
    this.ask();
  }

  private optimisticUserMessage(content: string): AIMessage {
    return { id: `pending-${Date.now()}`, role: 'user', content, provider: '', created_at: new Date().toISOString() };
  }

  private scrollToEnd(): void {
    setTimeout(() => this.transcriptEnd?.nativeElement.scrollIntoView({ behavior: 'smooth' }), 50);
  }

  private handleError(err: unknown): void {
    this.isSending.set(false);
    const message =
      (err as { error?: { error?: { message?: string } } })?.error?.error?.message ?? 'Something went wrong.';
    this.snackBar.open(message, 'Dismiss', { duration: 4000 });
  }
}
