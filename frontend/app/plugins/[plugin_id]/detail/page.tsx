import React from "react";
import {
    Container,
    Paper,
    Typography,
    List,
    ListItem,
    ListItemText,
    Button,
} from "@mui/material";
import Box from "@mui/material/Box";
import {PluginDetailsResponse} from "../../models";
import ExternalLink from "@/components/ExternalLink";
import {fixThatArrayWithNullShit, formatCurrency, formatNumber} from "@/utils";
import dynamic from "next/dynamic";
import ListBoxOneLine from "@/components/ListBoxOneLine";
import NoResultsFound from "@/components/NoResultsFound";
import PluginTimeseriesChart from "../../PluginTimeseriesChart";
import {fetchPluginTimeseries} from "../../driver";
import NextLink from "next/link";
import {marketplaceNameToHref} from "../../../marketplaces/models";
import RatingStarsWithText from "@/components/RatingStarsWithNumber";

const BoxWithInnerHtml = dynamic(
    () => import('@/components/BoxWithInnerHtml'),
    { ssr: false }  // This will disable server-side rendering for the component
);

const baseUrl = process.env.NEXT_PUBLIC_API_URL

// Function to fetch plugins details
async function fetchPluginDetails(plugin_id: string): Promise<PluginDetailsResponse | null> {
    const response = await fetch(`${baseUrl}/plugins/${plugin_id}/details`, {
        cache: "no-store", // Adjust caching as needed
    });

    if (!response.ok) {
        console.error(`Error fetching plugin details: ${response.statusText}`);
        return null;
    }

    return await response.json();
}

export default async function PluginDetailsPage({ params }: { params: { plugin_id: string } }) {
    const plugin = await fetchPluginDetails(params.plugin_id);
    if (!plugin) return <NoResultsFound model_name={`Plugin with id "${params.plugin_id}"`} />;

    const timeseriesData = await fetchPluginTimeseries(params.plugin_id);

    // FIX SHIT
    const lower_bound = fixThatArrayWithNullShit(plugin.revenue_lower_bound)
    const upper_bound = fixThatArrayWithNullShit(plugin.revenue_upper_bound)
    const reviews_summary_html = fixThatArrayWithNullShit(plugin.reviews_summary_html)
    const overview_summary_html = fixThatArrayWithNullShit(plugin.overview_summary_html)
    const revenue_analysis_html = fixThatArrayWithNullShit(plugin.revenue_analysis_html)

    const revenueRange = (lower_bound != null && upper_bound != null)
        ? `${formatCurrency(lower_bound)} - ${formatCurrency(upper_bound)}`
        : "N/A";

    // TODO(P1, ux): For chrome extensions, link it to extpose.com; for WP link it to plugin-rank ,. ...
    return (
        <Container maxWidth="md">
            <Paper elevation={3} style={{ padding: "2em", marginTop: "2em" }}>
                <Typography variant="h4" gutterBottom>
                    {plugin.name}
                </Typography>
                <List>
                    <ListItem>
                        <Box display="flex" alignItems="center" justifyContent="space-between" width="100%">
                            <Typography variant="body1">
                                <NextLink href={marketplaceNameToHref(plugin.marketplace_name)} passHref>
                                    <Button color="primary">
                                        {plugin.marketplace_name} Plugin
                                    </Button>
                                </NextLink>
                            </Typography>
                            <ExternalLink
                                href={plugin.marketplace_link || "#"}
                            >
                                {`See on ${plugin.marketplace_name} Marketplace`}
                            </ExternalLink>
                        </Box>
                    </ListItem>
                    <ListItem>
                        <ListItemText primary="Downloads" secondary={plugin.user_count ? `${formatNumber(plugin.user_count)}` : "N/A"} />
                        <ListItemText
                            primary="Ratings"
                            secondary={<RatingStarsWithText
                                rating={plugin.avg_rating}
                                ratingCount={plugin.rating_count}
                            />}
                            secondaryTypographyProps={{ component: 'div' }}
                        />
                        {plugin.propensity_to_rate ? <ListItemText
                            primary="Propensity to Rate"
                            secondary={`${formatNumber(plugin.propensity_to_rate)} ratings / 1000 downloads`}
                        /> : null}
                    </ListItem>
                    <ListItem>
                        <ListItemText primary="Revenue Estimate" secondary={revenueRange} />
                        <ListItemText
                            primary="Pricing Tiers"
                            secondary={<ListBoxOneLine listOfStrings={plugin.pricing_tiers} />}
                            secondaryTypographyProps={{ component: 'div' }}
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText
                            primary="Main Integrations"
                            secondary={<ListBoxOneLine listOfStrings={plugin.main_integrations} />}
                            secondaryTypographyProps={{ component: 'div' }}
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText
                            primary="Tags"
                            secondary={<ListBoxOneLine listOfStrings={plugin.tags} />}
                            secondaryTypographyProps={{ component: 'div' }}
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText primary={<strong>Developer</strong>} secondary={
                            <NextLink href={`/companies/${plugin.company_slug}/detail`} passHref>
                                <Button color="primary">{plugin.developer_name}</Button>
                            </NextLink>
                        } />
                        <ListItemText
                            primary="Listing Updated"
                            secondary={plugin.listing_updated ? new Date(plugin.listing_updated).toLocaleDateString() : "N/A"}
                        />
                    </ListItem>
                </List>

                {/* Timeseries Chart */}
                <Box mt={4}>
                    <Typography variant="h5" mb={2}>Historical Downloads & Ratings</Typography>
                    <PluginTimeseriesChart data={timeseriesData} />
                </Box>

                {/* Blog-style Content */}

                {plugin.elevator_pitch ? (
                    <Box mt={4}>
                        <Typography variant="h5" mb={2}>Elevator Pitch</Typography>
                        <Typography paragraph>{plugin.elevator_pitch}</Typography>
                    </Box>
                ) : null}
                {reviews_summary_html ? (
                    <BoxWithInnerHtml heading="Customers Say" htmlContent={reviews_summary_html} />
                ) : null}
                {overview_summary_html ? (
                    <BoxWithInnerHtml heading="Overview Summary" htmlContent={overview_summary_html} />
                ) : null}
                {revenue_analysis_html ? (
                    <BoxWithInnerHtml heading="Revenue Analysis" htmlContent={revenue_analysis_html} />
                ):null}
            </Paper>
        </Container>
    );
}
