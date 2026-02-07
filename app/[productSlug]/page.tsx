export default function ProductPage({
  params,
}: {
  params: { productSlug: string };
}) {
  return <div>my product page for {params.productSlug}</div>;
}
