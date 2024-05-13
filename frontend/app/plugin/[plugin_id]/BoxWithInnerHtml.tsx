import { Box, Typography } from '@mui/material';

interface BoxWithInnerHtmlProps {
  heading: string;
  htmlContent: string;  // Define the type for htmlContent
}

const BoxWithInnerHtml: React.FC<BoxWithInnerHtmlProps> = ({ heading, htmlContent }) => {
  return (
    <Box mt={4}>
      <Typography variant="h5">{heading}</Typography>
      <Typography paragraph dangerouslySetInnerHTML={{ __html: htmlContent }}>
      </Typography>
    </Box>
  );
}

export default BoxWithInnerHtml;
