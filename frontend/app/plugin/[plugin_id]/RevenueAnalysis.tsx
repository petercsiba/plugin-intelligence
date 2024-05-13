import { Box, Typography } from '@mui/material';

interface RevenueAnalysisProps {
  htmlContent: string;  // Define the type for htmlContent
}

const RevenueAnalysis: React.FC<RevenueAnalysisProps> = ({ htmlContent }) => {
  return (
    <Box mt={4}>
      <Typography variant="h5">Full Text Analysis</Typography>
      <Typography paragraph dangerouslySetInnerHTML={{ __html: htmlContent }}>
      </Typography>
    </Box>
  );
}

export default RevenueAnalysis;
