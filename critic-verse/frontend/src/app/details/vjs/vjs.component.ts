import {AfterViewInit, Component, ElementRef, Input, OnDestroy, OnInit, Renderer2, SimpleChanges, ViewChild, ViewEncapsulation} from '@angular/core';
import videojs from 'video.js';

@Component({
  selector: 'app-vjs',
  templateUrl: 'vjs.component.html',
  encapsulation: ViewEncapsulation.None
})

export class VjsComponent implements AfterViewInit, OnDestroy {
  @ViewChild('videoContainer', { static: true }) videoContainer!: ElementRef;
  @Input() options!: {
      fluid: boolean,
      autoplay: boolean,
      controls: boolean,
      sources: [{}]
  };
  @Input() source!: string | undefined;
  @Input() thumbnail!: string | undefined;
  @Input() type!: string | 'application/x-mpegURL';
  
  videoElement: any;

  constructor(private renderer: Renderer2) {} 

  player: any;

  createVjsPlayer() {
    this.videoElement = this.renderer.createElement('video');
    this.renderer.setAttribute(this.videoElement, 'class', 'video-js');
    this.renderer.setAttribute(this.videoElement, 'controls', 'true');
    this.renderer.setAttribute(this.videoElement, 'muted', 'true');
    this.renderer.setAttribute(this.videoElement, 'playsinline', 'true');
    this.renderer.setAttribute(this.videoElement, 'preload', 'none');
    const dataSetup = {
      poster: this.thumbnail,
    };
    this.renderer.setAttribute(this.videoElement, 'data-setup', JSON.stringify(dataSetup));
    this.renderer.setAttribute(this.videoElement, 'style', 'min-width: 300px !important; min-height: 150px !important; border-radius: 10px !important;');
    this.renderer.appendChild(this.videoContainer.nativeElement, this.videoElement);
  }

  ngAfterViewInit() {
    // Set up the Video.js player
    if(this.source != null)
      this.options.sources = [{src: this.source, type: this.type, quality: 'high'}];

    this.createVjsPlayer();

    this.player = videojs(this.videoElement, this.options, this.onPlayerReady.bind(this));
  }

  ngOnChanges(changes: SimpleChanges) {
    
    if(changes['source']) {
      this.source = changes['source'].currentValue;
      
      if (this.player) {
        this.player.dispose();
        this.createVjsPlayer();
      }
    }
    if(changes['type']) {
      this.type = changes['type'].currentValue;
    }

    this.options.sources = [{src: this.source, type: this.type, quality: 'high'}];
    if(this.videoElement) {
      this.player = videojs(this.videoElement, this.options, this.onPlayerReady.bind(this));
      this.player.on('error', (error: any) => {
        console.error('Video.js Error:', error);
        this.player.dispose();
      });
    }
  }

  onPlayerReady() {
    if(this.player) {
      //console.log('Player is ready');
    }
  }

  // Dispose the player OnDestroy
  ngOnDestroy() {
    if (this.player) {
      this.player.dispose();
    }
  }
}