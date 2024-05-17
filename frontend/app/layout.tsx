import * as React from 'react';
import { ThemeProvider, makeStyles } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from '@/theme/theme';  // Ensure this theme path is correct
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from "@vercel/speed-insights/next";
import NavigationBar from "./NavigationBar";


export default function RootLayout(props: { children: React.ReactNode }) {
  return (
      <html lang="en">
      <body>
      <ThemeProvider theme={theme}>
        {/* CssBaseline to kickstart an elegant, consistent, and simple baseline to build upon. */}
        <CssBaseline />
        <NavigationBar />
        {props.children}
        <Analytics />
        <SpeedInsights />
      </ThemeProvider>
      </body>
      </html>
  );
}
