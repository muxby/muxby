export function Spinner({ center = false }: { center?: boolean }) {
  const spinner = <div className="spinner" role="status" aria-label="Loading" />;
  if (center) {
    return <div className="spinner-center">{spinner}</div>;
  }
  return spinner;
}
