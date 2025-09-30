package cmd

import (
	"errors"
	"fmt"

	"subnetter/internal/client"

	"github.com/spf13/cobra"
)

var cPrefixID string
var cMask int
var cCount int

var carveCmd = &cobra.Command{
	Use:   "carve-children",
	Short: "Carve child prefixes under a parent prefix",
	RunE: func(cmd *cobra.Command, args []string) error {
		if cPrefixID == "" {
			return errors.New("--prefix-id is required")
		}
		if cMask == 0 {
			cMask = 28
		}
		if cCount <= 0 {
			cCount = 1
		}
		cl := client.New(baseURL, idemKey)
		kids, err := cl.CarveChildren(cPrefixID, cMask, cCount)
		if err != nil {
			return err
		}
		fmt.Printf("Carved %d children under %s:\n", len(kids), cPrefixID)
		for _, k := range kids {
			fmt.Printf("  - %s (id=%s)\n", k.CIDR, k.ID)
		}
		return nil
	},
}

func init() {
	rootCmd.AddCommand(carveCmd)
	carveCmd.Flags().StringVar(&cPrefixID, "prefix-id", "", "parent prefix UUID (required)")
	carveCmd.Flags().IntVar(&cMask, "mask", 28, "new prefix length")
	carveCmd.Flags().IntVar(&cCount, "count", 1, "number of child prefixes")
}
