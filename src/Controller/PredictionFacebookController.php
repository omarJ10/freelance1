<?php

namespace App\Controller;

use App\Service\FlaskIntegrationService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Contracts\HttpClient\HttpClientInterface;

class PredictionFacebookController extends AbstractController
{
    private $httpClient;

    public function __construct(HttpClientInterface $httpClient)
    {
        $this->httpClient = $httpClient;
    }

    #[Route('/predict/facebook', name: 'predict', methods: ['GET', 'POST'])]
    public function predict(Request $request): Response
    {
        $user = $this->getUser();

        $error = null;
        $bestHour = null;

        // Liste des options pour le champ "type_content"
        $typeContentOptions = ['text', 'video', 'image, text', 'event'];

        if ($request->isMethod('POST')) {
            $typeContent = $request->request->get('type_content');
            $totalEngagement = $request->request->get('total_engagement');

            if (!$typeContent || !$totalEngagement) {
                $error = "Veuillez remplir tous les champs.";
            } else {
                try {
                    // Appeler l'API Flask
                    $response = $this->httpClient->request('POST', 'http://127.0.0.1:5000/predict', [
                        'json' => [
                            'type_content' => $typeContent,
                            'totalEngagement' => (float) $totalEngagement,
                        ],
                    ]);

                    $data = $response->toArray();

                    if (isset($data['error'])) {
                        $error = $data['error'];
                    } else {
                        $bestHour = $data['best_hour'];
                    }
                } catch (\Exception $e) {
                    $error = "Erreur lors de la communication avec l'API Flask : " . $e->getMessage();
                }
            }
        }
        $user = $this->getUser();
        // Rendre la vue Twig
        return $this->render('prediction_facebook/index.html.twig', [
            'error' => $error,
            'username' => $user->getUsername(),
            'best_hour' => $bestHour,
            'type_content_options' => $typeContentOptions,
            'type_content' => $typeContent ?? '', // Valeur par défaut si aucune donnée
            'total_engagement' => $totalEngagement ?? '', // Valeur par défaut si aucune donnée// Passer les options à la vue
        ]);
    }
}
