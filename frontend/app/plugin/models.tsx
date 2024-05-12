export interface TopPluginResponse {
  id: number;
  name: string;
  link: string;
  img_logo_link: string;
  plugin_type: string;
  user_count: number;
  rating?: string;
  rating_count?: number;
  revenue_lower_bound?: number;
  revenue_upper_bound?: number;
  lowest_paid_tier: number | null;
  main_tags?: string[];
}

export interface PluginDetailsResponse {
    id: number;
    plugin_type: string;
    name: string;
    google_id: string;
    link?: string;

    user_count: number;
    rating?: string;
    rating_count?: number;

    full_text_analysis_html?: string;
    pricing_tiers?: string[];
    lowest_paid_tier: number | null;
    lower_bound?: number;
    upper_bound?: number;

    elevator_pitch?: string;
    main_integrations?: string;
    overview_summary?: string;
    search_terms?: string;
    tags?: string;

    created_at: string;
    updated_at?: string;
}
