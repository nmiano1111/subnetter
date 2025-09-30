package cmd

import (
	"errors"
	"fmt"

	"subnetter/internal/client"

	"github.com/spf13/cobra"
)

var nPrefixID string

var nextIPCmd = &cobra.Command{
	Use:   "next-ip",
	Short: "Allocate the next IP inside a prefix",
	RunE: func(cmd *cobra.Command, args []string) error {
		if nPrefixID == "" {
			return errors.New("--prefix-id is required")
		}
		cl := client.New(baseURL, idemKey)
		ip, err := cl.NextIP(nPrefixID)
		if err != nil {
			return err
		}
		fmt.Printf("Allocated IP: %s (id=%s)\n", ip.Address, ip.ID)
		return nil
	},
}

func init() {
	rootCmd.AddCommand(nextIPCmd)
	nextIPCmd.Flags().StringVar(&nPrefixID, "prefix-id", "", "prefix UUID (required)")
}
