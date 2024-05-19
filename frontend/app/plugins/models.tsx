import {MarketplaceName} from "../marketplaces/models";

export interface TopPluginResponse {
  id: number;
  name: string;
  marketplace_name: string;
  marketplace_link: string;
  img_logo_link?: string;

  user_count: number;
  avg_rating?: number;
  rating_count?: number;

  revenue_lower_bound?: number;
  revenue_upper_bound?: number;
  lowest_paid_tier: number | null;
  main_tags?: string[];
}

export interface PluginDetailsResponse {
    id: number;
    name: string;
    marketplace_name?: MarketplaceName;
    marketplace_id: string;
    marketplace_link: string;
    img_logo_link?: string;

    user_count: number;
    avg_rating?: number;
    rating_count?: number;

    company_slug?: string;
    developer_name?: string;

    revenue_analysis_html?: string;
    pricing_tiers?: string[];
    lowest_paid_tier: number | null;
    revenue_lower_bound?: number;
    revenue_upper_bound?: number;

    elevator_pitch?: string;
    main_integrations?: string[];
    overview_summary?: string;
    overview_summary_html?: string;
    reviews_summary?: string;
    reviews_summary_html?: string;
    tags?: string[];

    created_at: string;
    updated_at?: string;
}

export interface PluginTimeseriesData {
    marketplace_id: string
    p_date: Date
    user_count: number
    avg_rating?: number
    rating_count?: number
}
