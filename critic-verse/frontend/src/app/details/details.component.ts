import { Component, EventEmitter, Input, Output, SimpleChanges } from '@angular/core';

@Component({
    selector: 'app-details',
    templateUrl: './details.component.html'
})
export class DetailsComponent {
    videoSource: string = '';
    videoType: string = 'application/x-mpegURL';
    backgroundImageUrl: string = 'assets/not_found.jpg';
    description: string = 'No description available.';
    crew: string = '';
    genre: string = '';
    countries: string = '';
    platforms: string = '';
    companies: string = '';
    thumbnail: string = '';
    show_credits: boolean = false;
    credits_text: string = 'Show credits';

    @Input() item: any | null;

    @Output() closeDrawerEvent = new EventEmitter<void>();

    showCredits() {
        this.show_credits = !this.show_credits;
        if(this.show_credits)
            this.credits_text = 'Hide credits';
        else
            this.credits_text = 'Show credits';
    }

    ngOnInit() {
        if(this.item !== undefined) {
            if(this.item.summary !== null)
                this.description = this.item.summary;

            if(this.item?.video != null) {
                this.backgroundImageUrl = 'assets/not_found.jpg';
                this.videoSource = (this.item.video !== null ? this.item.video : 'https://file-examples.com/storage/fe1734aff46541d35a76822/2017/04/file_example_MP4_1920_18MG.mp4' );
                this.thumbnail = (this.item.video_thumbnail !== null ? this.item.video_thumbnail : '' );
                this.videoType = (this.item.video_type !== null ? this.item.video_type : 'video/mp4' );
            }
        }
    }

    ngOnChanges(changes: SimpleChanges) {
        if(changes['item'].currentValue) {
            this.backgroundImageUrl = (changes['item'].currentValue.images.length > 0 ? changes['item'].currentValue.images[1] : 'assets/not_found.jpg');
            this.description = (changes['item'].currentValue.summary !== null ? changes['item'].currentValue.summary : 'No description available.' );
            this.crew = (changes['item'].currentValue.crew !== null ? changes['item'].currentValue.crew.join(', '): '' );
            this.genre = (changes['item'].currentValue.genre !== null ? "&bull; " + changes['item'].currentValue.genre : '' );
            this.countries = (changes['item'].currentValue.countries !== null ? "&bull; " +changes['item'].currentValue.countries.join(',').replaceAll(",", "<br />&bull; ") : '' );
            this.platforms = (changes['item'].currentValue.platforms !== null ? "&bull; " +changes['item'].currentValue.platforms.join(',').replaceAll(",", "<br />&bull; ") : '' );
            this.companies = (changes['item'].currentValue.companies !== null ? "&bull; " +changes['item'].currentValue.companies.join(',').replaceAll(",", "<br />&bull;") : '' );
            this.videoSource = (changes['item'].currentValue.video !== null ? changes['item'].currentValue.video : '');
            this.thumbnail = (changes['item'].currentValue.video_thumbnail !== null ? changes['item'].currentValue.video_thumbnail : '');
            this.videoType = (changes['item'].currentValue.video_type !== null ? changes['item'].currentValue.video_type : "application/x-mpegURL" );  
            this.item = changes['item'].currentValue;  
        }   
    }



    closeDrawer() {
        this.closeDrawerEvent.emit();
    }
}