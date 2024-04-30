// TODO(P2): Decide on this
// Consider adding an _app.tsx in the pages directory if you need to customize the Next.js App component.
// This is useful for integrating global styles, layout components, or context providers that should apply to all pages.

// import React from 'react';
// import { AppProps } from 'next/app';
// import RootLayout from '../app/layout';  // Make sure the import path is correct
// import { ThemeProvider } from '@mui/material/styles';
// import CssBaseline from '@mui/material/CssBaseline';
// import theme from '../theme';  // Adjust path as necessary
//
// import '../styles/globals.css';  // Path to your global styles, if any
//
// function MyApp({ Component, pageProps }: AppProps) {
//   return (
//     <ThemeProvider theme={theme}>
//       <CssBaseline />  // Ensures a consistent baseline style across browsers
//       <RootLayout>
//         <Component {...pageProps} />
//       </RootLayout>
//     </ThemeProvider>
//   );
// }
//
// export default MyApp;