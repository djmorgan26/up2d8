import { Skeleton } from "./ui/skeleton";
import { GlassCard } from "./GlassCard";

export const ArticleSkeleton = () => {
  return (
    <GlassCard>
      <div className="space-y-3">
        <Skeleton className="h-6 w-3/4 bg-muted/50" />
        <Skeleton className="h-4 w-full bg-muted/50" />
        <Skeleton className="h-4 w-5/6 bg-muted/50" />
        <div className="flex justify-between pt-2">
          <Skeleton className="h-3 w-24 bg-muted/50" />
          <Skeleton className="h-3 w-16 bg-muted/50" />
        </div>
      </div>
    </GlassCard>
  );
};

export const FeedSkeleton = () => {
  return (
    <GlassCard>
      <div className="flex items-center justify-between">
        <div className="flex-1 space-y-2">
          <Skeleton className="h-5 w-48 bg-muted/50" />
          <Skeleton className="h-3 w-64 bg-muted/50" />
        </div>
        <Skeleton className="h-9 w-20 bg-muted/50" />
      </div>
    </GlassCard>
  );
};
