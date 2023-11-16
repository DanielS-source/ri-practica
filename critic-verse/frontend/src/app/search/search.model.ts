import { environment } from "src/environments/environment";

export type IPData = {
    ip: string;
    network: string;
    version: string;
    city: string;
    region: string;
    regionCode: string;
    country: string;
    countryName: string;
    countryCode: string;
    countryCodeIso: string;
    countryCapital: string;
    countryTld: string;
    continentName: string;
    continentCode: string;
    inEU: boolean;
    postalCode: string;
    geolocation: {
        latitude: number,
        longitude: number
    };
    timeZone: string;
    utcOffset: string;
    countryCallingCode: string;
    currency: string;
    currencyName: string;
    languages: string[];
    countryArea: number;
    countryPopulation: number;
    asn: string;
    org: string;
};

export type SearchItem = {
    time: number;
    size: number;
    page: number;
    n_pages: number;
    n_hits: number;
    items: GameItem[];
};

export type GameItem = {
    title: string;
    title_search: string;
    title_keyword: string;
    url: string;
    summary: string;
    genre: string[];
    metascore: string;
    user_score: string;
    release_date: string;
    companies: string[];
    images: string[];
    sentiment: string;
    must_play: boolean;
    crew: string[];
    countries: string[];
    platforms: string[];
    rating: string;
    official_site: string;
    video: string;
    video_type: string;
};

export interface SuggestionQuery {
    title?: string | null;
};

export interface GameQuery {
    title?: string | null;
    title_asc?: boolean | null;
    genre?: string | null;
    platform?: string | null;
    genres?: string | null; // Temporary
    platforms?: string | null; // Temporary
    country?: string | null;
    metascore_min?: number | null;
    metascore_max?: number | null;
    //critic_reviews_min?: number | null;
    //critic_reviews_max?: number | null;
    metascore_asc?: boolean | null;
    user_score_min?: number | null;
    user_score_max?: number | null;
    //user_reviews_min?: number | null;
    //user_reviews_max?: number | null;
    user_score_asc?: boolean | null;
    start_date?: Date | string | null;
    end_date?: Date | string | null;
    date_asc?: boolean | null;
    sort_by?: string | null;
    sort_direction?: string | null;
    page?: number | null;
    size?: number | null;
};

// You can also set default values as needed:
export const defaultGameQuery: GameQuery = {
    page: 0,
    size: environment.pageSize, // Assuming PAGE_SIZE is defined somewhere
};
