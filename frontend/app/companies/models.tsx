// ListResponse might have been a better name for this interface
export interface CompaniesTopResponse {
    slug: string;
    display_name: string;
    website_url?: string;
    img_logo_link?: string;
    count_plugin?: number;
    sum_download_count?: number;
    avg_avg_rating?: number;
}



export interface CompanyDetailsResponse {
    slug: number;
    display_name: string;
    legal_name: string;
    website_url?: string;
    type?: string;  // ONE_TRICK_PONY, SMALL_TEAM, LARGE_TEAM, ENTERPRISE

    //
    email_exists: boolean;  // Premium feature, only display if we have it
    address_exists: boolean;  // Premium feature, only display if we have it

    // Objective Aggregated Data
    count_plugin?: number;
    sum_download_count?: number;
    sum_rating_count?: number;
    weighted_avg_avg_rating?: number;

    // TODO: Derive these from GPT-3
    tags?: string;
    overview_summary_html?: string;
}
