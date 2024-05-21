export enum MarketplaceName {
    GOOGLE_WORKSPACE = "Google Workspace",
    CHROME_EXTENSION = "Chrome Extension",
}

export function marketplaceNameToHref(marketplaceName: MarketplaceName | null | undefined): string {
    if (!marketplaceName) {
        return '';
    }
    return "/marketplaces/" + marketplaceName
        .replace(/([a-z])([A-Z])/g, '$1_$2') // Add underscore between lower and upper case letters
        .replace(/\s+/g, '_') // Replace spaces with underscores
        .toLowerCase(); // Convert to lowercase
}


export interface MarketplaceStatsResponse {
    marketplace_name: string;
    total_plugins?: number;
    total_downloads?: number;
    total_ratings?: number;
    avg_downloads?: number;
    weighted_avg_rating?: number;
    median_lowest_paid_tier?: number;
    propensity_to_rate?: number;
}