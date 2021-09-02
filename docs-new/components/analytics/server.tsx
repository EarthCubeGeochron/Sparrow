export function analyticsHeaderScripts() {
  const GA_TRACKING_ID = process.env.NEXT_PUBLIC_GA_TRACKING_ID;
  if (GA_TRACKING_ID == null) return [];
  return [
    <script
      async
      src={`https://www.googletagmanager.com/gtag/js?id=${GA_TRACKING_ID}`}
    />,
    <script
      dangerouslySetInnerHTML={{
        __html: `
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${GA_TRACKING_ID}', {
            page_path: window.location.pathname,
          });
        `,
      }}
    />,
  ];
}
