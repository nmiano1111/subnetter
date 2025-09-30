package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var (
	baseURL string
	idemKey string
)

var rootCmd = &cobra.Command{
	Use:   "ipamctl",
	Short: "CLI for the IPAM FastAPI service",
	Long:  "Cobra CLI to exercise the IPAM API (tenants, VRFs, prefixes, IPs).",
}

func Execute() {
	// Allow env overrides
	if v := os.Getenv("IPAM_BASE_URL"); v != "" && baseURL == "" {
		baseURL = v
	}
	if k := os.Getenv("IDEMPOTENCY_KEY"); k != "" && idemKey == "" {
		idemKey = k
	}
	if baseURL == "" {
		baseURL = "http://127.0.0.1:8000"
	}
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
}

func init() {
	rootCmd.PersistentFlags().StringVar(&baseURL, "base-url", "", "API base URL (env: IPAM_BASE_URL)")
	rootCmd.PersistentFlags().StringVar(&idemKey, "idem", "", "Idempotency-Key header (env: IDEMPOTENCY_KEY)")
}
