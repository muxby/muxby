export function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="state-panel" role="alert">
      <div className="state-title">Something went wrong</div>
      <div>{message}</div>
      {onRetry && (
        <button
          type="button"
          className="btn"
          style={{ marginTop: 14 }}
          onClick={onRetry}
        >
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({
  title,
  message,
}: {
  title: string;
  message: string;
}) {
  return (
    <div className="state-panel">
      <div className="state-title">{title}</div>
      <div>{message}</div>
    </div>
  );
}
