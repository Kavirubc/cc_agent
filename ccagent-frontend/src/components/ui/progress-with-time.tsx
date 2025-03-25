// components/ui/progress-with-time.tsx
"use client"

import { useState, useEffect } from 'react'
import { Progress } from '@/components/ui/progress'
import { Card, CardContent } from '@/components/ui/card'
import prettyMilliseconds from 'pretty-ms'

interface ProgressWithTimeProps {
    progress: number
    remainingTime?: number | null
    agent?: string
    task?: string
}

export function ProgressWithTime({
    progress,
    remainingTime,
    agent,
    task
}: ProgressWithTimeProps) {
    const [displayProgress, setDisplayProgress] = useState(0)

    useEffect(() => {
        // Animate progress
        const timer = setTimeout(() => {
            setDisplayProgress(progress)
        }, 100)

        return () => clearTimeout(timer)
    }, [progress])

    return (
        <Card className="mb-4">
            <CardContent className="pt-6">
                {agent && task && (
                    <div className="mb-2 flex justify-between items-center">
                        <div className="font-medium">{agent}</div>
                        <div className="text-sm text-muted-foreground">{task}</div>
                    </div>
                )}

                <Progress value={displayProgress} className="h-2 mb-2" />

                <div className="flex justify-between text-sm">
                    <div>{displayProgress.toFixed(0)}% Complete</div>
                    {remainingTime !== null && remainingTime !== undefined && (
                        <div className="text-muted-foreground">
                            {prettyMilliseconds(remainingTime * 1000, { compact: true })} remaining
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    )
}
