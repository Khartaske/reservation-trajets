import { CurrencyPipe, DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject, signal } from '@angular/core';

interface Trip {
  id: number;
  origin: string;
  destination: string;
  departure_at: string;
  arrival_at: string | null;
  price: number;
  capacity: number;
  remaining_seats: number;
}

@Component({
  selector: 'app-root',
  imports: [DatePipe, CurrencyPipe],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
  private readonly http = inject(HttpClient);

  readonly trips = signal<Trip[]>([]);
  readonly loading = signal(true);
  readonly error = signal('');

  ngOnInit(): void {
    this.http.get<{ trips: Trip[] }>('/api/trips').subscribe({
      next: (response) => {
        this.trips.set(response.trips);
        this.loading.set(false);
      },
      error: () => {
        this.error.set("Impossible de charger les trajets. Vérifiez que l'API est démarrée.");
        this.loading.set(false);
      },
    });
  }
}
